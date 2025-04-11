import utils as pcd_utils

from .global_registration import run_fast_global_registration, run_global_registration
from .icp import ICP


def run_pipeline(source, target, voxel_size=0.05):
    result = run_global_registration(source, target, voxel_size)

    pcd_utils.draw_registration_result(source, target, result.transformation)

    distance_threshold = voxel_size * 0.4

    icp = ICP(source, target, result.transformation, threshold=distance_threshold)

    print("parametros do icp: ", icp.get_params())

    transformation = icp.execute()

    pcd_utils.draw_registration_result(source, target, transformation)


if __name__ == "__main__":
    path_pcd1 = r"C:\Users\EMC\Documents\GitHub\TCC_\fusion_harvardPointCloud.ply"
    pcd1 = pcd_utils.load_point_cloud(path_pcd1)

    path_pcd2 = r"C:\Users\EMC\Documents\GitHub\TCC_\fusion_harvard_intrinsicPointCloud.ply"
    pcd2 = pcd_utils.load_point_cloud(path_pcd2)

    run_pipeline(pcd1, pcd2)
