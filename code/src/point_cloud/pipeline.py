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
