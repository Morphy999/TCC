import argparse
import numpy as np
import open3d as o3d
import os
import sys
from datetime import datetime

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    
print(sys.path) 

from global_registration import run_fast_global_registration, run_global_registration
from icp import ICP
import utils as pcd_utils


def run_pipeline(source, target, voxel_size=0.05, only_icp=False):
    
    distance_threshold = 0.5
    
    initial_transformation = None
    
    if not only_icp:
        distance_threshold = float(voxel_size) * 0.4
        result = run_global_registration(source, target, voxel_size)
        initial_transformation = result.transformation

    icp = ICP(source = source, target = target, threshold=distance_threshold, type="point_to_point", initial_transformation=initial_transformation)
    
    print("parametros do icp: ", icp.get_params())

    transformation = icp.execute()
    
    print("transformation: ", transformation)
    
    return transformation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Point cloud registration pipeline")
    parser.add_argument("pcd1_path", type=str, help="Path to the first point cloud")
    parser.add_argument("pcd2_path", type=str, help="Path to the second point cloud")
    parser.add_argument("--voxel_size", type=float, default=0.05, help="Voxel size for downsampling")
    parser.add_argument("--only_icp", action="store_true", help="Run only ICP registration without global registration")
    parser.add_argument("--output", type=str, help="Path to save the transformed point cloud")
    
    args = parser.parse_args()
    
    pcd1 = pcd_utils.load_point_cloud(args.pcd1_path)
    pcd2 = pcd_utils.load_point_cloud(args.pcd2_path)
    
    transformation = run_pipeline(pcd1, pcd2, voxel_size=args.voxel_size, 
                                 only_icp=args.only_icp)
    
    save_transformed_point_cloud(pcd1, transformation, args.output)