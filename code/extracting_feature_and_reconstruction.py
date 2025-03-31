import argparse
import shutil
from pathlib import Path
import enlighten
import pycolmap
import subprocess
from pycolmap import logging
import numpy as np
import os

def add_camera_to_database(database_path, intrinsic_file, width, height, image_paths):
    print("Resetando banco de dados...")


    db_file = Path(database_path)
    if db_file.exists():
        db_file.unlink()  
    db = pycolmap.Database(database_path)

    print("Adicionando parâmetros intrínsecos da câmera ao banco de dados...")

    
    K = np.loadtxt(intrinsic_file)
    fx, fy = K[0, 0], K[1, 1]  # Focal lengths
    cx, cy = K[0, 2], K[1, 2]  

    # Criar um objeto de câmera
    camera = pycolmap.Camera.create(
        camera_id=1,  
        model=pycolmap.CameraModelId.PINHOLE,  
        focal_length=fx,  
        width=width,
        height=height
    )
    
    camera.principal_point_x = cx
    camera.principal_point_y = cy

    camera_id = db.write_camera(camera)

    image_paths = list(image_paths.glob('*.jpg'))  

    for path in image_paths:
        if path.exists():
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
        with manager.counter(
            total=num_images, desc="Images registered:"
        ) as pbar:
            pbar.update(0, force=True)
            reconstructions = pycolmap.incremental_mapping(
                database_path,
                image_path,
                sfm_path,
                initial_image_pair_callback=lambda: pbar.update(2),
                next_image_callback=lambda: pbar.update(1),
            )
    return reconstructions


def run(output_path, intrinsic_file):
    
    

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
        add_camera_to_database(database_path, intrinsic_file, width=1920, height=1080, image_paths=image_path) 
             
    print("extract features")
    pycolmap.extract_features(database_path, image_path,device = pycolmap.Device(1))
    print("exhaustive match images")
    pycolmap.match_exhaustive(database_path)

    if sfm_path.exists():
        shutil.rmtree(sfm_path)
    sfm_path.mkdir(exist_ok=True)

    recs = incremental_mapping_with_pbar(database_path, image_path, sfm_path)
    
    print("-----------------------------------------------------reconstruction---------------------------------------------------------")

    for idx, rec in recs.items():
        logging.info(f"#{idx} {rec.summary()}")
        
    pycolmap.undistort_images(mvs_path, sfm_path / '0', image_path)
    pycolmap.patch_match_stereo(mvs_path)  
    pycolmap.stereo_fusion(mvs_path / "fusion.ply", mvs_path)
    if pycolmap.poisson_meshing(mvs_path/"fusion.ply",mvs_path/'mesh.ply'):
        print("reconstruido com sucesso")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the script with an output path and optional camera intrinsics.")
    parser.add_argument("output_path", type=str, help="Path to the output directory")
    parser.add_argument("intrinsic_path", type=str, nargs="?", default="None", help="Path to the camera intrinsic file (opcional)")

    args = parser.parse_args()

    run(args.output_path, args.intrinsic_path)