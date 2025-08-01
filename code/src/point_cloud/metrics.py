import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree


def load_point_cloud(path):
    pcd = o3d.io.read_point_cloud(path)
    return np.asarray(pcd.points)


def get_dist_kdtree(pc1, pc2, k=1):
    tree1 = cKDTree(pc1)
    tree2 = cKDTree(pc2)
    dist1, _ = tree2.query(pc1, k=k)
    dist2, _ = tree1.query(pc2, k=k)
    return dist1, dist2


def chamfer_distance_bidirectional(pc1, pc2):
    dist1, dist2 = get_dist_kdtree(pc1, pc2, k=1)

    chamfer = np.mean(dist1**2) + np.mean(dist2**2)
    return chamfer, dist1, dist2


def hausdorff_distance(pc1, pc2):
    dist1, dist2 = get_dist_kdtree(pc1, pc2, k=1)

    hausdorff = max(np.max(dist1), np.max(dist2))
    return hausdorff


if __name__ == "__main__":
    path1 = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\Open3d\sala_chance_simple.ply"
    path2 = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\Open3d\sala_no_chance_simple.ply"

    pc1 = load_point_cloud(path1)
    pc2 = load_point_cloud(path2)

    print("Calculando metricas...")

    chamfer, dists1, dists2 = chamfer_distance_bidirectional(pc1, pc2)
    print(f"Chamfer Distance (bidirecional): {chamfer:.6f}")
    print(f"  - Média das distâncias (1 → 2): {np.mean(dists1):.6f}")
    print(f"  - Média das distâncias (2 → 1): {np.mean(dists2):.6f}")
    print(f"  - MSE (1 → 2): {np.mean(dists1 ** 2):.6f}")
    print(f"  - MSE (2 → 1): {np.mean(dists2 ** 2):.6f}")
    print(f"  - Desvio padrão (1 → 2): {np.std(np.concatenate([dists1, dists2])):.6f}")
    print(f"  - Desvio padrão (2 → 1): {np.std(dists2):.6f}")
    print(f"  - Desvio padrão total: {np.std(np.concatenate([dists1, dists2])):.6f}")

    hausdorff = hausdorff_distance(pc1, pc2)
    print(f"Hausdorff Distance: {hausdorff:.6f}")
