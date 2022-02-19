import numpy as np
import cv2 as cv
import torch
import math
import os

model1 = torch.hub.load('ultralytics/yolov5', 'custom', path='./model1.pt', force_reload=True)

files = os.listdir('./NewData_p2')

for file in files:

    img = cv.imread('./NewData_p2/' + file)

    print(img.shape)

    robot_list = model1(img)
    robot_list = robot_list.pandas().xyxy[0].to_numpy()

    for robot in robot_list:
        x1, y1, x2, y2 = robot[0], robot[1], robot[2], robot[3]
        x1_ = math.floor(x1)
        y1_ = math.floor(y1)
        x2_ = math.ceil(x2)
        y2_ = math.ceil(y2)
        img_cropped = img[y1_:y2_, x1_:x2_]

        cv.imwrite('cropped/' + file, img_cropped)

#        cv.rectangle(img, (x1_,y1_), (x2_,y2_), (255,252,0), 1)
        
#    cv.imwrite('./test_res/' + file, img)

    print('=== Cropped and saved', file)
