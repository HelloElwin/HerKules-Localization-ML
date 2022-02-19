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

fn = plf.Freenect2()
num_of_device = fn.enumerateDevices()
serial = fn.getDefaultDeviceSerialNumber()
device = fn.openDevice(serial)

types = plf.FrameType.Color | plf.FrameType.Ir | plf.FrameType.Depth
listener = plf.SyncMultiFrameListener(types)
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()
print(1)
m = device.getIrCameraParams()
fx, fy, cx, cy = m.fx, m.fy, m.cx, m.cy
np.save("c_m.npy", np.array([fx, fy, cx, cy]))
device.stop()
device.close()
