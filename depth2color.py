import numpy as np
import pylibfreenect2 as plf
import open3d as o3d
import cv2 as cv
depth = np.load("depth.npy")
#cv.imshow("da", depth)
#cv.waitKey(0)
color = np.load("color.npy")
#cv.imshow("da", color)
#cv.waitKey(0)

#fn = plf.Freenect2()
#num_of_device = fn.enumerateDevices()
#serial = fn.getDefaultDeviceSerialNumber()
#device = fn.openDevice(serial)
#
#types = plf.FrameType.Color | plf.FrameType.Ir | plf.FrameType.Depth
#listener = plf.SyncMultiFrameListener(types)
#device.setColorFrameListener(listener)
#device.setIrAndDepthFrameListener(listener)
#
#device.start()
#m = device.getIrCameraParams()
# fx, fy, cx, cy = m.fx, m.fy, m.cx, m.cy
# np.save("cameramatrix.npy", np.array([fx, fy, cx, cy]))
def d_t_p(depth,color):
    fx, fy, cx, cy = np.load("c_m.npy")
    h, w = np.mgrid[0:424,0:512]
    zz = depth/1000
    xx = (w - cx) * zz / fx
    yy = (h - cy) * zz / fy
    xyz = np.dstack((xx,yy,zz)).reshape(-1,3)
    color = color.reshape(-1,3)
    color = color/255
    color = color[...,::-1]
    print(xyz.shape)
    print(color.shape)
    cnt = 0
    for i in color:
        m = max(i)
        if m>0: cnt += 1
    print("cnt: ", cnt)
    cv.imwrite("depth_with_color.jpg", color.reshape(424, 512, 3))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(-xyz)
    pcd.colors = o3d.utility.Vector3dVector(color)
    #num = 20
    #istd = 2.0
    #pcd, ind = pcd.remove_statistical_outlier(num,std)
    #o3d.visualization.draw_geometries([pcd])
    #o3d.io.write_point_cloud("pcd_pcd.ply",pcd)
    return pcd
    #device.stop()
    #device.close()
