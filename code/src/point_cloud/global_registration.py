import open3d as o3d
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import utils as pcd_utils


def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd_utils.voxel_downsampling(pcd, voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30)
    )

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down, o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100)
    )
    return pcd_down, pcd_fpfh


def execute_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down,
        target_down,
        source_fpfh,
        target_fpfh,
        True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3,
        [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold),
        ],
        o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999),
    )
    return result


def execute_fast_global_registration(
    source_down, target_down, source_fpfh, target_fpfh, voxel_size
):
    distance_threshold = voxel_size * 0.5
    print(":: Apply fast global registration with distance threshold %.3f" % distance_threshold)
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down,
        target_down,
        source_fpfh,
        target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold
        ),
    )
    return result


def run_global_registration(source, target, voxel_size=0.05):
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)

    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    result = execute_global_registration(
        source_down, target_down, source_fpfh, target_fpfh, voxel_size
    )

    return result


def run_fast_global_registration(source, target, voxel_size=0.05):
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)

    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    result = execute_fast_global_registration(
        source_down, target_down, source_fpfh, target_fpfh, voxel_size
    )


if __name__ == "__main__":
    path_pcd1 = r"C:\Users\EMC\Documents\GitHub\TCC_\fusion_harvardPointCloud.ply"
    pcd1 = pcd_utils.load_point_cloud(path_pcd1)

    path_pcd2 = r"C:\Users\EMC\Documents\GitHub\TCC_\fusion_harvard_intrinsicPointCloud.ply"
    pcd2 = pcd_utils.load_point_cloud(path_pcd2)

    result = run_global_registration(pcd1, pcd2)

    print(result)

    pcd_utils.draw_registration_result(pcd1, pcd2, result.transformation)
