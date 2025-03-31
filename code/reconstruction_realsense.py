import argparse
import subprocess
import shutil
import json
from pathlib import Path
from tqdm import tqdm
import shutil

# Configuração do parser de argumentos
parser = argparse.ArgumentParser(description="Processamento de vídeo e reconstrução 3D.")
parser.add_argument("--image", type=str, help="Caminho para a pasta de imagens (modo imagem)")
parser.add_argument("--teste", type=str, help="Número de teste para criação dos diretórios")
parser.add_argument("--overwrite",action="store_true")

args = parser.parse_args()

modo_imagem = args.image is not None
entrada_path = Path(args.image)

teste = args.teste

host_base_path = Path(f"/homeLocal/walterbueno/TCC/reconstrucao/{teste}")

def clean_and_create(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

if args.overwrite: 
    clean_and_create(host_base_path)

config_path = host_base_path / "config"
config_path.mkdir(parents=True, exist_ok=True)

src_intrinsic = Path("/homeLocal/walterbueno/TCC/calibracao/camera_intrinsic.json")
dest_intrinsic = host_base_path / "camera_intrinsic.json"

if src_intrinsic.exists():
    shutil.copy2(src_intrinsic, dest_intrinsic)
    print(f"Arquivo {src_intrinsic} copiado para {dest_intrinsic}")
else:
    print(f"Aviso: Arquivo {src_intrinsic} não encontrado.")


print("copiando dataset para reconstruçao")
for folder in ["color", "depth"]:
    src_folder = entrada_path / folder
    dest_folder = host_base_path / folder

    if src_folder.exists():
        dest_folder.mkdir(parents=True, exist_ok=True)
        files = list(src_folder.rglob("*"))

        for file in tqdm(files, desc=f"Copiando {folder}", unit="file"):
            if file.is_file():  
                rel_path = file.relative_to(src_folder)  
                dest_file = dest_folder / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file) 

realsense_example_path = Path("/homeLocal/walterbueno/TCC/realsense/realsense_example.json")
realsense_json_path = config_path / "realsense.json"

with open(realsense_example_path, 'r') as file:
    config_data = json.load(file)
    
config_data["path_dataset"] = f"/container/reconstrucao/{teste}"
config_data["path_intrinsic"] = f"/container/reconstrucao/{teste}/camera_intrinsic.json"

print("config path dataset", config_data['path_dataset'])

with open(realsense_json_path, 'w') as file:
    json.dump(config_data, file, indent=4)

singularity_container = "/homeLocal/walterbueno/TCC/open3d_sandbox/"

command = [
    "sudo", "singularity", "exec", "--nv",
    "--bind", f"{host_base_path}:/container/reconstrucao/{teste}",
    "--bind", "/homeLocal/walterbueno/TCC/Open3D:/root/Open3D",
    "--bind", "/homeLocal/walterbueno/TCC/calibracao/:/containter/calibracao",
    "--bind", f"/homeLocal/walterbueno/TCC/reconstrucao/{teste}/:/container/reconstrucao/{teste}",
    singularity_container, 
    "python3", "/root/Open3D/examples/python/reconstruction_system/run_system.py",
    "--config", f"/container/reconstrucao/{teste}/config/realsense.json",  
    "--make", "--register", "--refine", "--integrate", "--device", "CUDA:0"
]

subprocess.run(command)

for folder in ["color", "depth"]:
    dest_folder = host_base_path / folder
    if dest_folder.exists():
        shutil.rmtree(dest_folder)
        
print("Processo completo.")
