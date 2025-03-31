import argparse
# import pycolmap
import numpy as np
import open3d as o3d

# Configuração do argparse para capturar os parâmetros de linha de comando
parser = argparse.ArgumentParser(description="Visualização da nuvem de pontos a partir de uma reconstrução.")
parser.add_argument("reconstruction_path", type=str, help="Caminho para o diretório de reconstrução")
args = parser.parse_args()

# Usando o caminho passado como argumento
reconstruction_path = args.reconstruction_path

# Carregar a reconstrução
# reconstruction = pycolmap.Reconstruction(reconstruction_path)

# # Obter os pontos 3D da reconstrução
# points3d = np.array([points.xyz for points in reconstruction.points3D.values()])

# # Exibir a forma dos pontos 3D
# print(points3d.shape)

# # Criar a nuvem de pontos no Open3D
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points3d)

# # Visualizar a nuvem de pontos
# o3d.visualization.draw_geometries([pcd])


point_cloud = o3d.io.read_point_cloud(args.reconstruction_path)

# Verificar se a nuvem de pontos foi carregada corretamente
if point_cloud.is_empty():
    print("Erro: O arquivo .ply está vazio ou não foi carregado corretamente.")
else:
    print("Nuvem de pontos carregada com sucesso!")

# Exibir informações da nuvem de pontos
print(point_cloud)

# Visualizar a nuvem de pontos
o3d.visualization.draw_geometries([point_cloud], 
                                  window_name="Visualização Dense PLY",
                                  width=800, height=600,
                                  point_show_normal=True,
                                  mesh_show_wireframe=True)
