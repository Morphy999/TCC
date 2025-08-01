import argparse
import copy
from datetime import datetime

import rootutils

root_path = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import src.point_cloud.utils as pcd_utils
from src.point_cloud.global_registration import (
    run_fast_global_registration,
    run_global_registration,
)
from src.point_cloud.icp import ICP


def run_pipeline(source, target, voxel_size=0.05, only_icp=False):
    distance_threshold = 0.5

    initial_transformation = None

    if not only_icp:
        distance_threshold = float(voxel_size) * 0.4
        result = run_fast_global_registration(source, target, voxel_size)
        initial_transformation = result.transformation

        pcd_utils.save_transformed_point_cloud(
            source,
            initial_transformation,
            output_path=r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\initial_transformation.ply",
        )

    icp = ICP(
        source=source,
        target=target,
        threshold=distance_threshold,
        type="point_to_point",
        initial_transformation=initial_transformation,
    )

    print("parametros do icp: ", icp.get_params())

    transformation = icp.execute()

    print("transformation: ", transformation)

    return transformation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Point cloud registration pipeline")
    parser.add_argument("pcd1_path", type=str, help="Path to the first point cloud")
    parser.add_argument("pcd2_path", type=str, help="Path to the second point cloud")
    parser.add_argument(
        "--voxel_size", type=float, default=0.05, help="Voxel size for downsampling"
    )
    parser.add_argument(
        "--only_icp",
        action="store_true",
        help="Run only ICP registration without global registration",
    )
    parser.add_argument("--output", type=str, help="Path to save the transformed point cloud")

    args = parser.parse_args()

    pcd1 = pcd_utils.load_point_cloud(args.pcd1_path)
    pcd2 = pcd_utils.load_point_cloud(args.pcd2_path)

    transformation = run_pipeline(pcd1, pcd2, voxel_size=args.voxel_size, only_icp=args.only_icp)

    save_transformed_point_cloud(pcd1, transformation, args.output)
