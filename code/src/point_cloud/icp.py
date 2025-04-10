import copy

import numpy as np
import open3d as o3d
import rootutils
import utils as pcd_utils

root_path = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from src.utils.timer_measure import timer_measure


class ICP:
    def __init__(
        self, source, target, threshold=0.02, type="point_to_point", initial_transformation=None
    ):
        self.source = source
        self.target = target
        self.threshold = threshold
        self.type = type
        self.initial_transformation = (
            initial_transformation if initial_transformation is not None else np.identity(4)
        )

    @timer_measure
    def execute(self):
        if self.type == "point_to_plane":
            reg_icp = o3d.pipelines.registration.registration_icp(
                self.source,
                self.target,
                self.threshold,
                self.initial_transformation,
                o3d.pipelines.registration.TransformationEstimationPointToPlane(),
                o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000),
            )
            return reg_icp.transformation

        elif self.type == "point_to_point":
            reg_icp = o3d.pipelines.registration.registration_icp(
                self.source,
                self.target,
                self.threshold,
                self.initial_transformation,
                o3d.pipelines.registration.TransformationEstimationPointToPoint(),
                o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000),
            )
            return reg_icp.transformation

        else:
            raise ValueError("Invalid ICP type. Choose 'point_to_point' or 'point_to_plane'.")

    def draw_registration_result(self, transformation):
        source_temp = copy.deepcopy(self.source)
        target_temp = copy.deepcopy(self.target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(transformation)
        pcd_utils.visualize_point_cloud([source_temp, target_temp])


if __name__ == "__main__":
    path_pcd1 = r"C:\Users\EMC\Documents\GitHub\TCC_\fusion_harvardPointCloud.ply"
    pcd1 = pcd_utils.load_point_cloud(path_pcd1)

    path_pcd2 = r"C:\Users\EMC\Documents\GitHub\TCC_\fusion_harvard_intrinsicPointCloud.ply"
    pcd2 = pcd_utils.load_point_cloud(path_pcd2)

    icp = ICP(pcd1, pcd2, threshold=0.02, type="point_to_plane")

    transformation = icp.execute()

    print("Transformation Matrix:\n", transformation)

    icp.draw_registration_result(transformation)
