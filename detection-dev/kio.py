import torch                                                                                         
import numpy
import padding
import pandas as pd
import cv2 as cv
import math
import os

def inference(img):
    model1 = torch.hub.load('ultralytics/yolov5', 'custom', path='./model1.pt', force_reload=True)
    model2 = torch.hub.load('ultralytics/yolov5', 'custom', path='./model2.pt', force_reload=True)
    robot_list = model1(img)
    robot_list = robot_list.pandas().xyxy[0].to_numpy()
    ret = {}
    for robot in robot_list:
        if robot[-1] != 'robot': continue
        x1, y1, x2, y2 = robot[0], robot[1], robot[2], robot[3]
        if robot[-1] not in ret:
            ret[robot[-1]] = []
        x1_ = math.floor(x1)
        y1_ = math.floor(y1)
        x2_ = math.ceil(x2)
        y2_ = math.ceil(y2)
        ret[robot[-1]].append((x1_,y1_,x2_,y2_))
        img_cropped = img[y1_:y2_, x1_:x2_]
        feature_list = model2(img_cropped)
        feature_list = feature_list.pandas().xyxy[0].to_numpy()

        for feature in feature_list:
            if feature[-1] not in ret:
                ret[feature[-1]] = []
            x11, y11, x22, y22 = feature[0], feature[1], feature[2], feature[3]
            ret[feature[-1]].append((math.floor(x1+x11),math.floor(y1+y11), math.ceil(x1+x22), math.ceil(y1+y22)))
     return ret

if __name__ == '__main__':
    img =cv.imread('img38.png')
    inference(img)
   # files = os.listdir("./w55/RGBdata")
 
    #for file in files:
     #   img = cv.imread("./w55/RGBdata/" + file)
      #  inference(img, file)

   # print("完全没问题哦！")
