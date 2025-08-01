import numpy as np
import open3d as o3d

pcd1_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_cut3r_clean.ply"
pcd2_path = r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_chance_cut3r_clean.ply"

source = o3d.io.read_point_cloud(pcd1_path)
target = o3d.io.read_point_cloud(pcd2_path)

source_bb = source.get_axis_aligned_bounding_box()
target_bb = target.get_axis_aligned_bounding_box()

source_scale = np.linalg.norm(source_bb.get_extent())
target_scale = np.linalg.norm(target_bb.get_extent())

scale_factor = target_scale / source_scale

source_scaled = source.scale(scale_factor, center=source_bb.get_center())

o3d.io.write_point_cloud(
    r"C:\Users\EMC\Documents\TCC arquivos\Sala Lab\sala_cut3r_scaled.ply", source_scaled
)
