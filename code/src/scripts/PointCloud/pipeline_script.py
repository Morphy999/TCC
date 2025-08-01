import time

import open3d as o3d
import rootutils

root_path = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import src.point_cloud.utils as pcd_utils
from src.point_cloud.chance_detection_heat import detect_changes_with_heatmap
from src.point_cloud.pipeline import run_pipeline

if __name__ == "__main__":
    pcd1_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_chance_cut3r_clean.ply"
    pcd2_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_cut3r_clean.ply"
    output_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_cut3r_transformed_icp.ply"

    pcd1 = pcd_utils.load_point_cloud(pcd1_path)
    pcd2 = pcd_utils.load_point_cloud(pcd2_path)

    pcd1 = pcd_utils.scale_point_cloud(pcd1, pcd2)

    start_time = time.time()

    transformation = run_pipeline(pcd1, pcd2, voxel_size=0.05, only_icp=True)

    pcd_utils.save_transformed_point_cloud(pcd1, transformation, output_path)

    end_time = time.time()
    print(f"Tempo de execução: {end_time - start_time} segundos")

    threshold = 0.5

    heatmap_pcd = detect_changes_with_heatmap(output_path, pcd2_path, threshold)

    o3d.io.write_point_cloud(
        r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\heatmap_change_pcd_cut3r_{}.ply".format(
            threshold
        ),
        heatmap_pcd,
    )
