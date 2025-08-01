import argparse
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image

# Configuração do parser de argumentos
parser = argparse.ArgumentParser(description="Processamento de vídeo e reconstrução 3D.")
parser.add_argument("--image", type=str, help="Caminho para a pasta de imagens (modo imagem)")
parser.add_argument("--video", type=str, help="Caminho para o arquivo de vídeo (modo vídeo)")
parser.add_argument("--teste", type=str, help="Número de teste para criação dos diretórios")
parser.add_argument("--num_teste", type=int, default=1, help="Downsampling frames (padrão: 1)")
parser.add_argument("--intrinsic", type=str, help="nome do arquivo .txt personalizado")
parser.add_argument(
    "--resize",
    nargs=2,
    type=int,
    metavar=("WIDTH", "HEIGHT"),
    help="Nova resolução das imagens redimensionadas (ex: --resize 1024 768)",
)


args = parser.parse_args()

if args.image and args.video:
    parser.error("Não pode usar --image e --video ao mesmo tempo. Escolha um.")

if not args.image and not args.video:
    parser.error("É necessário especificar --image ou --video.")

modo_imagem = args.image is not None
entrada_path = Path(args.image if modo_imagem else args.video)
teste = args.teste
n = args.num_teste

output_folder = Path(f"/homeLocal/walterbueno/TCC/video_frames/{teste}")
host_base_path = Path(f"/homeLocal/walterbueno/TCC/reconstrucao/{teste}")
images_path = host_base_path / "images"

intrinsic_name = Path(args.intrinsic) if args.intrinsic else "None"

for path in [output_folder, host_base_path]:
    if path.exists():
        shutil.rmtree(path)

output_folder.mkdir(parents=True, exist_ok=True)
host_base_path.mkdir(parents=True, exist_ok=True)
images_path.mkdir(parents=True, exist_ok=True)

if not modo_imagem:
    print("Executando o script de processamento de vídeo...")
    subprocess.run(["python3", "cut_video.py", str(entrada_path), str(output_folder), str(n)])

print(
    f"Copiando arquivos de {output_folder if not modo_imagem else entrada_path} para {images_path}..."
)
for file in (output_folder if not modo_imagem else entrada_path).glob("*"):
    shutil.copy(file, images_path)

resize = args.resize
scale = 1.0

if resize:
    first_image = next(images_path.glob("*.jpg"), None)
    if first_image is None:
        raise ValueError("Nenhuma imagem encontrada para calcular escala.")

    with Image.open(first_image) as img:
        original_width, original_height = img.size

    new_width, new_height = resize
    scale_x = new_width / original_width
    scale_y = new_height / original_height

    if abs(scale_x - scale_y) > 1e-3:
        raise ValueError("A proporção da nova resolução não bate com a original.")

    scale = scale_x
    print(f"Escala de redimensionamento calculada: {scale:.4f}")

print("iniciando SINGULARITY")
singularity_container = "/homeLocal/walterbueno/TCC/colmap_cuda_80/"
cmd = [
    "singularity",
    "exec",
    "--nv",
    "--bind",
    "/homeLocal/walterbueno/TCC/code/:/container/codigo",
    "--bind",
    f"/homeLocal/walterbueno/TCC/reconstrucao/{teste}:/container/reconstrucao/{teste}",
    "--bind",
    "/homeLocal/walterbueno/TCC/calibracao/:/container/calibracao",
    singularity_container,
    "python3",
    "/container/codigo/extracting_feature_and_reconstruction.py",
    f"/container/reconstrucao/{teste}",
    f"/container/calibracao/{intrinsic_name}",
    "--scale",
    str(scale),
]

start = time.time()
subprocess.run(cmd)
end = time.time()

print(f"Tempo total de execução: {end - start:.2f} segundos, ou {(end - start) / 60:.2f} minutos.")
print("Processo completo.")
