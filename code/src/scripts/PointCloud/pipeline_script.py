import subprocess

singularity_container = "/homeLocal/walterbueno/TCC/open3d_sandbox/"
print("iniciando singularity")
command = [
    "singularity",
    "exec",
    "--nv",
    "--bind",
    "/homeLocal/walterbueno/TCC/Open3D:/root/Open3D",
    "--bind",
    "/homeLocal/walterbueno/TCC_/code/src/:/container/code/src",
    "--bind",
    "/homeLocal/walterbueno/TCC_/Data/PointCloud/:/container/data/point_cloud",
    singularity_container,
    "python3",
    "/container/code/src/point_cloud/pipeline.py",
    "/container/data/point_cloud/fusion_sala_clean_finalized.ply",
    "/container/data/point_cloud/fusion_sala_chance_clean_finalized.ply",
    "--only_icp",
    "--output",
    "/container/data/point_cloud/fusion_sala_clean_finalized_transformed.ply",
]

subprocess.run(command)