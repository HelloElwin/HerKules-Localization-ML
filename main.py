import rospy as ros
import polar as plr
import detection
import numpy as np
import time
import cv2 as cv
from sensor_msgs.msg import Image as S_image
import ros_numpy
import open3d as o3d
import paint
import depth2color as d_t_p

class Grabber():
    def __init__(self):

        self.depth_f = True
        self.color_f = True
        self.c_f = True
        self.depth = np.zeros((424,512))
        self.color = np.zeros((1080,1920))
        self.c = np.zeros((424,512))

        self.model = detection.Model()
        self.model.load()
        self.finder = plr.Finder()

        self.time = time.time()

        ros.init_node("Grabber")
#        self.subscriber1 = ros.Subscriber("/kinect2/sd/image_depth_rect", S_image, self.depthCallback)
#        self.subscriber2 = ros.Subscriber("/kinect2/hd/image_color", S_image, self.colorCallback)
        self.subscriber1 = ros.Subscriber("depth", S_image, self.depthCallback, queue_size=1)
        self.subscriber2 = ros.Subscriber("color", S_image, self.colorCallback, queue_size=1)

        ros.spin()

    def depthCallback(self,depth_msg):
        if self.depth_f == True:
#            self.depth = ros_numpy.image.image_to_numpy(depth_msg)
            self.depth = np.frombuffer(depth_msg.data, dtype=np.float32).reshape(424, 512)
#            cv.imshow("depth", self.depth)
#            cv.waitKey(0)
#            self.depth = self.depth[:depth.shape[0]//2]
            self.depth_f = False


    def colorCallback(self,color_msg):
        if self.color_f == True:
            self.color_f = False
#            self.depth_f = False
            t00 = time.time()
            self.color = np.frombuffer(color_msg.data, dtype=np.uint8).reshape(1080, 1920, 4)
            self.color = self.color[:,:,:3]
#            cv.imshow("color", self.color)
#            cv.waitKey(0)
#            self.color = ros_numpy.image.image_to_numpy(color_msg)
        
            t0 = time.time()
            print(f"===finished grabbing, time={t0-t00}")

            c_map = self.finder.generate(self.depth)

#            print("shape of cmap-----------", c_map.shape)
            color0 = self.color.reshape(-1,3)
            color1 = np.zeros((424, 512, 3))
            for i in range(424):
                for j in range(512):
                    if c_map[i][j] == np.inf or c_map[i][j] == np.nan: c_map[i][j] = 0
                    if c_map[i][j] < 0 or c_map[i][j] >= 1920 * 1080: continue
                    color1[i][j] = color0[int(c_map[i][j])]
#            np.save("color.npy", color1)

            t1 = time.time()
            print(f"===finished mapping, time={t1-t0}")

            bboxes = self.model.inference(self.color)
            t2 = time.time()
            print(f"===finished inferencing, time={t2-t1}")
            print("-----Boxes are", bboxes)

            candidates = self.finder.findbbox(c_map, bboxes, self.depth)
            t3 = time.time()
            print(f"===finished candidates, time={t3-t2}")
            print("-----Candidates are:", candidates)

            xyz = self.finder.depth2xyz_prepare(self.depth, candidates)
#            print(xyz)

            can = []
            for i in xyz:
                for j in xyz[i]:
                    can.append(j)
            pcd = d_t_p.d_t_p(self.depth,color1)
#            np.save("can.npy", np.array(can))
            paint.show_painting(pcd, can)
            
           # pcd = o3d.geometry.PointCloud()
            
           # pcd.points = o3d.utility.Vector3dVector()
           # pcd.colors = o3d.utility.Vector3dVector(self.c)
           # o3d.visualization.draw_geometried([pcd])
           # o3d.io.write_point_cloud("pcdpcdpcd.ply",pcd)

#            np.save("depth.npy",self.depth)

            print(f"===finished one frame, time={time.time()-self.time}")
            self.time = time.time()
            self.color_f = True
            self.depth_f = True

if __name__ == '__main__':
    Grab = Grabber()
