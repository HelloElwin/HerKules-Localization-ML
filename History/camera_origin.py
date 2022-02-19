import pylibfreenect2 as plf
import numpy as np
import cv2 as cv
import time

class Camera():

	fn = plf.Freenect2()
	num_of_device = fn.enumerateDevices()
	serial = fn.getDefaultDeviceSerialNumber()
	device = fn.openDevice(serial)

	types = plf.FrameType.Color | plf.FrameType.Ir | plf.FrameType.Depth
	listener = plf.SyncMultiFrameListener(types)
	device.setColorFrameListener(listener)
	device.setIrAndDepthFrameListener(listener)

	device.start()

	def __init__(self):
		pass

	def load(self, device, listener):
		self.dev = device
		self.lis = listener
		self.reg = plf.Registration(self.dev.getIrCameraParams(),
									self.dev.getColorCameraParams())
	def translate(self, un, re):
		points = np.zeros((512 * 424, 3))
		colors = np.zeros((512 * 424, 3))
		cnt = 0
		timefor = time.time()
		for i in range(512):
			for j in range(424):
				x, y, z, b, g, r = self.reg.getPointXYZRGB(un, re, i, j)
				if np.isnan(x): x, y, z = self.n, self.n, self.n
				points[i * 424 + j][0] = x
				points[i * 424 + j][1] = y
				points[i * 424 + j][2] = z
				colors[i * 424 + j][0] = r / 255
				colors[i * 424 + j][1] = g / 255
				colors[i * 424 + j][2] = b / 255
		timefor = time.time()
		pcd = o3d.geometry.PointCloud()
		timevector = time.time()
		pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
		pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
        	timevector = time.time() - timevector
		time_end = time.time()
		return timevector

	def grab(self):

		time_start = time.time()
		frames = plf.FrameMap()
		print(self.lis, self.dev, self.reg)
		self.lis.waitForNewFrame(frames)
		print("===Got new frame", time.time() - time_start)

		color = frames[plf.FrameType.Color]
		depth = frames[plf.FrameType.Depth]
		hongw = frames[plf.FrameType.Ir]

		cv.imwrite('test_color.jpg', color.asarray(dtype=np.uint8))
		cv.imwrite('test_depth.jpg', depth.asarray(dtype=np.float32))
		np.save('test_color.npy', color.asarray(dtype=np.uint8))
		np.save('test_depth.npy', depth.asarray(dtype=np.float32))

		undistorted = plf.Frame(512, 424, 4)
		registered = plf.Frame(512, 424, 4)
		bigdepth = plf.Frame(1920, 1082, 4)
		color_depth_map = np.zeros((424, 512), np.int32)
		re = self.reg.apply(color, depth, undistorted, registered, bigdepth=bigdepth, color_depth_map=color_depth_map.ravel())

		np.save('img.npy', depth.asarray(dtype=np.float32))

#		print(type(bigdepth)) 
#		print(color_depth_map.shape)
#		cv.imwrite('./bigdepth.jpg', bigdepth.asarray(dtype=np.float32))
#		cv.imwrite('./bbbdepth.jpg', color_depth_map)

#		np.save('img.npy', bigdepth)

#		self.reg.undistortDepth(depth, undistorted)

		self.lis.release(frames)

		return depth.asarray()
	
	def nan_cnt(self, x):
		total, cnt = 0, 0
		for i in x:
			for j in i:
				total += 1
				if np.isnan(j): cnt += 1
		print("===total:", total, "nan:", cnt, "nan_rate:", cnt / total)
	
	def noise_reduction(self, pcd):
		num_neighbors = 24
		std_ratio = 1.65
		sor_pcd, ind = pcd.remove_statistical_outlier(num_neighbors, std_ratio)
		return sor_pcd

	def plane_partition(self, pcd):
		distance_threshold = 0.5
		ransac_n = 10
		num_iterations = 1000
		plane_model, inliers = pcd.segment_plane(distance_threshold, ransac_n, num_iterations)
		inlier_cloud = pcd.select_by_index(inliers)
		return inlier_cloud

	def show(self, depth):
		pass
		print(np.sum(depth))
		depth = depth * 100
		depth = depth.astype(np.int8)
		cv.imshow("depth", depth)

if __name__ == '__main__':
    cam1 = Camera()
    cam1.load(cam1.device, cam1.listener)
    cnt = 0
#        while True:
#		t0 = time.time()
#	#	depth = cam1.grab()
#		rgbd = cam1.grab()
#		#cam1.show(depth)
#		cnt += 1
#		print(rgbd)
#		if (cnt == 2): break
#		print(time.time() - t0)
