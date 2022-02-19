import ros_numpy
import cv2 as cv
import numpy as np
import rospy as ros
import open3d as o3d
import polar as plr
import detection
from PIL import Image
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import UInt8MultiArray
from sensor_msgs.msg import Image as msg_Image

class Collector():
    
    def __init__(self):

        self.sub1 = ros.Subscriber("/kinect2/sd/image_depth_rect", msg_Image, self.process_depth)
        self.sub2 = ros.Subscriber("/kinect2/hd/image_color_rect", msg_Image, self.process_color)
        self.sub3 = ros.Subscriber("/loc_c_map", UInt8MultiArray, self.process_what)
        self.pub1 = ros.Publisher("/loc_depth", Float32MultiArray, queue_size=1)

        self.color = None
        self.depth = None
        self.c_map = None

        self.model = detection.Model()
        self.model.load()

        self.finder = plr.Finder()

        ros.init_node("loc_collector")
        ros.sleep(1)
        ros.spin()

    def process_depth(self, depth_msg):
        depth = ros_numpy.image.image_to_numpy(depth_msg)
        self.depth = depth
        cv.imwrite("./depth.jpg", self.depth)
        depth = depth.flatten().astype(np.float32)
        depth_msg = Float32MultiArray()
        depth_msg.data = depth
#        print("====", np.array(depth_msg.data).sum())
        ros.loginfo(np.array(depth_msg.data).sum())
        self.pub1.publish(depth_msg)

    def process_color(self, image_msg):
        self.color = ros_numpy.image.image_to_numpy(image_msg)
        bboxes = self.model.inference(self.color)
        print("===got bboxes", bboxes)

    def process_what(self, c_map_msg):
        self.c_map = np.array(c_map_msg.data)
        print("===got c_map", self.c_map.shape)

if __name__ == '__main__':
    collector = Collector()
