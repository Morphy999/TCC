import copy
import os
import sys

import numpy as np
import open3d as o3d
import rootutils

root_path = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import src.utils as pcd_utils


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

    def get_params(self):
        return {
            "source": self.source,
            "target": self.target,
            "threshold": self.threshold,
            "type": self.type,
            "initial_transformation": self.initial_transformation,
        }

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
            print("executando icp point to point")

            reg_icp = o3d.pipelines.registration.registration_icp(
                self.source,
                self.target,
                self.threshold,
                self.initial_transformation,
                o3d.pipelines.registration.TransformationEstimationPointToPoint(),
                o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=5000),
            )
            return reg_icp.transformation

        else:
            raise ValueError("Invalid ICP type. Choose 'point_to_point' or 'point_to_plane'.")

    def draw_registration_result(self, transformation):
        pcd_utils.draw_registration_result(self.source, self.target, transformation)
