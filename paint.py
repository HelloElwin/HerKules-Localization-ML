import open3d as o3d
import numpy as np
def show_painting(pcd, candidates):

    p = np.asarray(pcd.points)
    c = np.asarray(pcd.colors)

    p = p.tolist()
    c = c.tolist()

    for cu in candidates:
        for x in [-0.002, -0.004, 0, 0.002, 0.004]:
            for y in [-0.002, -0.004, 0, 0.002, 0.004]:
                for z in [-0.002, -0.004, 0, 0.002, 0.004]:
#                    print(cu)
                    p.append(-1 * np.array([cu[0] + x, cu[1] + y, cu[2] + z]))
                    c.append(np.array([255, 0, 0]))

    pcd = o3d.geometry.PointCloud()

    pcd.points = o3d.utility.Vector3dVector(p)
    pcd.colors = o3d.utility.Vector3dVector(c)

    o3d.visualization.draw_geometries([pcd])

if __name__ == '__main__':
    pcd = o3d.io.read_point_cloud("./pcd_pcd.ply")
    candidates = np.load("./can.npy")
    show_painting(pcd, candidates)
