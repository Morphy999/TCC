import numpy as np
import open3d as o3d


def detect_changes_with_heatmap(pcd_path1, pcd_path2, threshold=0.3):
    pcd1 = o3d.io.read_point_cloud(pcd_path1)
    pcd2 = o3d.io.read_point_cloud(pcd_path2)

    pcd2_tree = o3d.geometry.KDTreeFlann(pcd2)

    distances = []

    for point in pcd1.points:
        [_, idx, dist] = pcd2_tree.search_knn_vector_3d(point, 1)
        distances.append(np.sqrt(dist[0]))

    distances = np.array(distances)

    normalized = np.clip(distances / threshold, 0.0, 1.0)

    def colormap(value):
        if value < 0.25:
            r = 0
            g = value / 0.25
            b = 1
        elif value < 0.5:
            r = (value - 0.25) / 0.25
            g = 1
            b = 1 - (value - 0.25) / 0.25
        elif value < 0.75:
            r = 1
            g = 1 - (value - 0.5) / 0.25 * 0.5
            b = 0
        else:
            r = 1
            g = 0.5 - (value - 0.75) / 0.25 * 0.5
            b = 0
        return [r, g, b]

    colors = np.array([colormap(v) for v in normalized])

    pcd1.colors = o3d.utility.Vector3dVector(colors)

    return pcd1


if __name__ == "__main__":
    pcd1_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_cut3r_transformed_icp.ply"
    pcd2_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_cut3r_clean.ply"

    threshold = 0.3
    heatmap_pcd = detect_changes_with_heatmap(pcd1_path, pcd2_path, threshold=threshold)

    o3d.io.write_point_cloud(
        r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\heatmap_change_pcd_cut3r_{}.ply".format(
            threshold
        ),
        heatmap_pcd,
    )
