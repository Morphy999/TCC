import argparse
import json
import shutil
import subprocess
from pathlib import Path

from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description="Processamento de vídeo e reconstrução 3D.")
    parser.add_argument("--image", type=str, help="Caminho para a pasta de imagens (color/depth)")
    parser.add_argument(
        "--rosbag", type=str, help="Caminho para o arquivo .bag (ativa modo rosbag)"
    )
    parser.add_argument(
        "--teste", type=str, required=True, help="Número de teste para criação dos diretórios"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Sobrescreve diretório de reconstrução se existir"
    )
    return parser.parse_args()


def clean_and_create(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_intrinsic_file(dest_path: Path):
    src_intrinsic = Path("/homeLocal/walterbueno/TCC/calibracao/camera_intrinsic.json")
    dest_intrinsic = dest_path / "camera_intrinsic.json"
    if src_intrinsic.exists():
        shutil.copy2(src_intrinsic, dest_intrinsic)
        print(f"Arquivo {src_intrinsic} copiado para {dest_intrinsic}")
    else:
        print(f"Aviso: Arquivo {src_intrinsic} não encontrado.")


def copy_dataset(entrada_path: Path, dest_base_path: Path):
    print("Copiando dataset para reconstrução")
    for folder in ["color", "depth"]:
        src_folder = entrada_path / folder
        dest_folder = dest_base_path / folder
        if src_folder.exists():
            dest_folder.mkdir(parents=True, exist_ok=True)
            files = list(src_folder.rglob("*"))
            for file in tqdm(files, desc=f"Copiando {folder}", unit="file"):
                if file.is_file():
                    rel_path = file.relative_to(src_folder)
                    dest_file = dest_folder / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest_file)


def copy_rosbag_file(bag_path: Path, dest_base_path: Path):
    dest_file = dest_base_path / "realsense.bag"
    print(f"Copiando arquivo .bag para {dest_file}")
    shutil.copy2(bag_path, dest_file)


def create_config_file(config_path: Path, teste: str, use_rosbag: bool):
    realsense_example_path = Path("/homeLocal/walterbueno/TCC/realsense/realsense_example.json")
    realsense_json_path = config_path / "realsense.json"

    with open(realsense_example_path, "r") as file:
        config_data = json.load(file)

    config_data["path_intrinsic"] = f"/container/reconstrucao/{teste}/camera_intrinsic.json"

    if use_rosbag:
        config_data["path_dataset"] = str(
            (Path(f"/container/reconstrucao/{teste}") / "realsense.bag").as_posix()
        )
    else:
        config_data["path_dataset"] = f"/container/reconstrucao/{teste}"

    print("Config path_dataset:", config_data["path_dataset"])

    with open(realsense_json_path, "w") as file:
        json.dump(config_data, file, indent=4)


def run_reconstruction_container(teste: str, host_base_path: Path):
    singularity_container = "/homeLocal/walterbueno/TCC/open3d_sandbox/"
    command = [
        "sudo",
        "singularity",
        "exec",
        "--nv",
        "--bind",
        f"{host_base_path}:/container/reconstrucao/{teste}",
        "--bind",
        "/homeLocal/walterbueno/TCC/Open3D:/root/Open3D",
        "--bind",
        "/homeLocal/walterbueno/TCC/calibracao/:/containter/calibracao",
        "--bind",
        f"/homeLocal/walterbueno/TCC/reconstrucao/{teste}/:/container/reconstrucao/{teste}",
        singularity_container,
        "python3",
        "/root/Open3D/examples/python/reconstruction_system/run_system.py",
        "--config",
        f"/container/reconstrucao/{teste}/config/realsense.json",
        "--make",
        "--register",
        "--refine",
        "--integrate",
        "--device",
        "CUDA:0",
    ]
    subprocess.run(command)


def cleanup_folders(base_path: Path, use_rosbag: bool):
    if use_rosbag:
        bag_file = base_path / "realsense.bag"
        if bag_file.exists():
            bag_file.unlink()
            print(f"Arquivo .bag removido: {bag_file}")
    else:
        for folder in ["color", "depth"]:
            folder_path = base_path / folder
            if folder_path.exists():
                shutil.rmtree(folder_path)
                print(f"Pasta removida: {folder_path}")


def main():
    args = parse_args()

    use_rosbag = args.rosbag is not None
    teste = args.teste
    host_base_path = Path(f"/homeLocal/walterbueno/TCC/reconstrucao/{teste}")
    config_path = host_base_path / "config"

    if args.overwrite:
        clean_and_create(host_base_path)

    config_path.mkdir(parents=True, exist_ok=True)
    copy_intrinsic_file(host_base_path)

    if use_rosbag:
        bag_path = Path(args.rosbag)
        if not bag_path.exists():
            print(f"Erro: arquivo .bag não encontrado em {bag_path}")
            return
        copy_rosbag_file(bag_path, host_base_path)
    else:
        if not args.image:
            print("Erro: parâmetro --image é obrigatório quando não estiver usando --rosbag.")
            return
        entrada_path = Path(args.image)
        copy_dataset(entrada_path, host_base_path)

    create_config_file(config_path, teste, use_rosbag)
    run_reconstruction_container(teste, host_base_path)
    cleanup_folders(host_base_path, use_rosbag)

    print("Processo completo.")


if __name__ == "__main__":
    main()
