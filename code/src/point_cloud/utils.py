import copy
from typing import List
import numpy as np
import open3d as o3d


def load_point_cloud(file_path):
    """
    Load a point cloud from a file.
    :param file_path: Path to the point cloud file.
    :return: Open3D point cloud object.
    """
    pcd = o3d.io.read_point_cloud(file_path)
    print(f"Número de pontos na nuvem: {len(pcd.points)}")
    return pcd


def voxel_downsampling(pcd, voxel_size=0.05):
    downpcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    return downpcd


def visualize_point_cloud(pcd_list: List):
    """
    Visualize a point cloud using Open3D.
    :param pcd: Open3D point cloud object.
    """
    o3d.visualization.draw_geometries(pcd_list)


def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    visualize_point_cloud([source_temp, target_temp])


def pcd_distance(pcd1, pcd2):
    """
    Compute the distance between two point clouds.
    :param pcd1: First point cloud.
    :param pcd2: Second point cloud.
    :return: Distance between the two point clouds.
    """
    dists = pcd1.compute_point_cloud_distance(pcd2)
    dists = np.asarray(dists)
    ind = np.where(dists > 0.01)

    print(ind)
    print("Number of points in pcd1 that are not in pcd2: ", len(ind[0]))

    return sum(dists) / len(dists)


def save_transformed_point_cloud(source, transformation, output_path=None):
    """
    Save the transformed point cloud to a file.
    
    Args:
        source: The source point cloud to transform and save
        transformation: The transformation matrix to apply
        output_path: Path to save the point cloud. If None, a default name will be generated.
    
    Returns:
        The path where the point cloud was saved
    """
    transformed_pcd = source.clone()
    transformed_pcd.transform(transformation)
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"transformed_pointcloud_{timestamp}.ply"
    
    o3d.io.write_point_cloud(output_path, transformed_pcd)
    print(f"Transformed point cloud saved to: {output_path}")
    
    return output_path