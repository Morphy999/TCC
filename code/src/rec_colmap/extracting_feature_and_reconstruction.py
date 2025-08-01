import argparse
import os
import shutil
import subprocess
from pathlib import Path

import enlighten
import numpy as np
import pycolmap
from PIL import Image
from pycolmap import logging


def add_camera_to_database(database_path, intrinsic_file, image_dir, scale=1):
    print("Resetando banco de dados...")

    db_file = Path(database_path)
    if db_file.exists():
        db_file.unlink()
    db = pycolmap.Database(database_path)

    print("Adicionando parâmetros intrínsecos da câmera ao banco de dados...")

    K = np.loadtxt(intrinsic_file)
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    # Aplica o fator de escala aos parâmetros intrínsecos
    fx *= scale
    fy *= scale
    cx *= scale
    cy *= scale

    # Assume que todas as imagens têm a mesma resolução após o redimensionamento
    sample_image_path = next(Path(image_dir).glob("*.jpg"))
    with Image.open(sample_image_path) as img:
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)

    camera = pycolmap.Camera.create(
        camera_id=1,
        model=pycolmap.CameraModelId.PINHOLE,
        focal_length=np.mean([fx, fy]),
        width=new_width,
        height=new_height,
    )

    camera.principal_point_x = cx
    camera.principal_point_y = cy
    camera.focal_length_x = fx
    camera.focal_length_y = fy

    camera_id = db.write_camera(camera)

    print("Adicionando imagens ao banco de dados...")

    image_paths = list(Path(image_dir).glob("*.jpg"))

    for path in image_paths:
        if path.exists():
            with Image.open(path) as img:
                resized = img.resize((new_width, new_height), Image.LANCZOS)
                resized.save(path)

            image = pycolmap.Image(
                name=path.name,
                camera_id=camera_id,
                points2D=pycolmap.ListPoint2D(),
            )
            db.write_image(image)
        else:
            print(f"Imagem não encontrada: {path}")

    db.close()
    print(f"Câmera adicionada ao banco de dados com ID {camera_id} e imagens associadas.")
    return camera_id


def incremental_mapping_with_pbar(database_path, image_path, sfm_path):
    num_images = pycolmap.Database(database_path).num_images
    with enlighten.Manager() as manager:
        with manager.counter(total=num_images, desc="Images registered:") as pbar:
            pbar.update(0, force=True)
            reconstructions = pycolmap.incremental_mapping(
                database_path,
                image_path,
                sfm_path,
                initial_image_pair_callback=lambda: pbar.update(2),
                next_image_callback=lambda: pbar.update(1),
            )
    return reconstructions


def run(output_path, intrinsic_file, scale):
    if intrinsic_file == "None" or not os.path.exists(intrinsic_file):
        print("⚠️ Nenhum arquivo de calibração foi fornecido. Continuando sem calibração.")
        intrinsic_file = None
    else:
        print("intrinsic file encontrado")

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output path: {output_path}")

    image_path = output_path / "images"
    database_path = output_path / "database.db"
    sfm_path = output_path / "sfm"
    mvs_path = output_path / "mvs"

    logging.set_log_destination(logging.INFO, output_path / "INFO.log")

    if not image_path.exists():
        print("Image path does not exist:", image_path)

    if database_path.exists():
        database_path.unlink()

    if intrinsic_file is not None:
        print("add camera intrinsic parameters to database")
        add_camera_to_database(database_path, intrinsic_file, image_path, scale)

    print("extract features")

    print("Device")
    device = pycolmap.Device(1)
    print(device.name)
    print(device.value)

    sift_options = pycolmap.SiftExtractionOptions(
        # estimate_affine_shape = True,
        # domain_size_pooling = True,
    )

    pycolmap.SiftMatchingOptions(
        guided_matching=True,
    )

    pycolmap.extract_features(database_path, image_path, device=device)

    print("exhaustive match images")
    pycolmap.match_exhaustive(database_path)

    if sfm_path.exists():
        shutil.rmtree(sfm_path)
    sfm_path.mkdir(exist_ok=True)

    recs = incremental_mapping_with_pbar(database_path, image_path, sfm_path)

    print(
        "-----------------------------------------------------reconstruction---------------------------------------------------------"
    )

    for idx, rec in recs.items():
        logging.info(f"#{idx} {rec.summary()}")

    print("undistort images")
    pycolmap.undistort_images(mvs_path, sfm_path / "0", image_path)
    print("patch match stereo")

    max_image_size = -1

    pm_options = pycolmap.PatchMatchOptions(max_image_size=max_image_size)

    stereo_options = pycolmap.StereoFusionOptions(
        max_image_size=max_image_size,
    )

    print("patch match stereo com opções customizadas")
    pycolmap.patch_match_stereo(workspace_path=mvs_path, options=pm_options)

    print("refine depth")

    pycolmap.stereo_fusion(mvs_path / "fusion.ply", mvs_path, options=stereo_options)

    print("saving fusion.ply")

    if pycolmap.poisson_meshing(mvs_path / "fusion.ply", mvs_path / "mesh.ply"):
        print("reconstruido com sucesso")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the script with an output path and optional camera intrinsics."
    )
    parser.add_argument("output_path", type=str, help="Path to the output directory")
    parser.add_argument(
        "intrinsic_path",
        type=str,
        nargs="?",
        default="None",
        help="Path to the camera intrinsic file (opcional)",
    )
    parser.add_argument("--scale", type=str, help="Scale factor for the images")

    args = parser.parse_args()

    scale = float(args.scale)

    run(args.output_path, args.intrinsic_path, scale)
