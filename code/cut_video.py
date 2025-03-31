import argparse
import cv2
import os
from pathlib import Path

parser = argparse.ArgumentParser(description="Extrair frames de um vídeo e salvar em uma pasta de saída.")
parser.add_argument("video_path", type=str, help="Caminho para o arquivo de vídeo")
parser.add_argument("output_folder", type=str, help="Caminho para a pasta onde os frames serão salvos")
parser.add_argument('num_frames',type = str, help='valor de N')
args = parser.parse_args()


video_path = args.video_path
output_folder = Path(args.output_folder)

os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)

frame_count = 0
frame_count_save = 0
n = int(args.num_frames)

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break

    if frame_count % n == 0:
        frame_filename = os.path.join(output_folder, f'image_{frame_count_save:04d}.png')
        cv2.imwrite(frame_filename, frame)
        frame_count_save += 1
    
    frame_count += 1

cap.release()
print(f'{frame_count_save} frames salvos em {output_folder}')
