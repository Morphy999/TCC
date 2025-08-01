import numpy as np
import open3d as o3d


def detect_changes(pcd_path1, pcd_path2, threshold=0.3):
    pcd1 = o3d.io.read_point_cloud(pcd_path1)
    pcd2 = o3d.io.read_point_cloud(pcd_path2)

    pcd2_tree = o3d.geometry.KDTreeFlann(pcd2)

    changed_points = []

    for point in pcd1.points:
        [_, idx, dist] = pcd2_tree.search_knn_vector_3d(point, 1)
        if dist[0] > threshold**2:
            changed_points.append(point)

    if changed_points:
        change_pcd = o3d.geometry.PointCloud()
        change_pcd.points = o3d.utility.Vector3dVector(np.array(changed_points))
        return change_pcd
    else:
        return None
