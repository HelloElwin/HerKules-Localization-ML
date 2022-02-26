# <div align="center">HerKules-Localization-ML</div>
This Github repository demonstrate the ML-based localization method for RoboMaster-AI.


Our idea is to find (if could) the ***the nearest points to the centers*** of the robot(s) itself/themselves and its/their feature(s). Original results are indexes of the points in the 1080\*1920-sized color-image numpy array. We then calculate the corresponding indexes of these points in the 424\*512-sized depth-image numpy array. The final results are generated with these corresponding indexes together with our depth-image map.


This method includes ROS publish and subscription, callback functions, YOLOv5, opencv, open3d, etc..

## <div align="center">Method</div>
Our localization pipeline consists of 5 parts:


* Grabbing color and depth images.
* Detecting robots in the color image.
* Detecting robot armors in the detected bounding boxes of robots.
* Computing 3D coordinates of the armors with the depth image.
* Sending out the coordinates.


In the following are the detailed description.


<details close>
<summary> <b> Image Grabbing </b> </summary>


We utilize **ROS** to grab real-time color and depth images from the Kinect2 video stream and send them to two callback functions. In the callback functions, we convert the raw image data to numpy arrays before further processing.


We establish a node named "Grabber".

```python
ros.init_node("Grabber")
```

Create two subcribers. 

```python
from sensor_msgs.msg import Image as S_image
depth_subscriber = ros.Subscriber("/kinect2/sd/image_depth_rect", S_image, self.depthCallback)
color_subscriber = ros.Subscriber("/kinect2/hd/image_color_rect", S_image, self.colorCallback)
```

Then convert the sensor message Image to numpy array for faster matrix computation later.

```python
depth = np.frombuffer(depth_msg.data, dtype=np.float32).reshape(424, 512)
color = np.frombuffer(color_msg.data, dtype=np.uint8).reshape(1080, 1920, 4)
```

To guarantee that the depth image and the color image we are dealing with are grabbed from the same time, we set two bool variables to indicate whether we have finished progressing the last frame and are able to progress the next one. 

The original value of these two variables are True. When we received one depth image, we translate the sensor message to numpy array and save it in `depth` before we set the `depth_flag` to False. The same is applied to `color_flag`.

When finished processing a frame, we set `depth_flag` and `color_flag` back to True.
  
```python
if depth_flag == True:
    depth = np.frombuffer(depth_msg.data, dtype=np.float32).reshape(424, 512)
    depth_flag = False
```

```python
if color_flag == True:
    color_flag = False
    color = np.frombuffer(color_msg.data, dtype=np.uint8).reshape(1080, 1920, 4)

    # further operations...

    color_flag = True
    depth_flag = True
```

</details>


<details close>
<summary> <b> Detection </b> </summary>


In this part, we detect the coordinates of the robots and their features.

Temporarily, we choose YOLOv5 to detect our objects for its considerable performance, flexible model size, and complete user guide.

***  
  
## [!IMPORTANT!] to be added
  
***

The trained models are stored in model1.pt and model2.pt respectively. We need to load these two models first.
  
```python
model1 = torch.hub.load('ultralytics/yolov5', 'custom', path='./model1.pt', force_reload=True)
model2 = torch.hub.load('ultralytics/yolov5', 'custom', path='./model2.pt', force_reload=True)
```

Applying `model1` to our grabbed color image, we can get the results and then translate it to numpy array.

```python
results = model1(color_image)
robot_results = results.pandas().xyxy[0].to_numpy()
```

`robot_results` contains the coordinates of the top-left and the bottom-right of each detected object with confidences and labels.

  
E.G.
  
```python
> print(list)
[[176.2563934326172 221.65625 261.8894958496094 303.94512939453125 0.9433885812759399 0 'robot']]
```
  
Hence, to increase the proportion of the armor we need to detect in the whole image, we cropped the original color image with the coordinates in `res`. The new color image is just the robot(s) itself/themselves.
  
  
Since the origin of the coordinate system is the top-left of the image, we can get the indexes directly from the coordinates. 

```python
for robot in robot_results:
    x1, y1, x2, y2 = robot[0], robot[1], robot[2], robot[3] 
      # robot[0]:the x-coordinate of top-left;robot[1]:the y-coordinate of top-left;robot[3]:the x-coordinate of bottom-right;robot[4]:the y-coordinate of bottom-right;
    x1_ = math.floor(x1)
    y1_ = math.floor(y1)
    x2_ = math.ceil(x2)
    y2_ = math.ceil(y2)
    img_cropped = color_image[y1_:y2_,x1_:x2_]
```

Then we apply `model2` to our cropped image and we get coordinates of different features.

```python
results = model2(img_cropped)
feature_results = results.pandas().xyxy[0].to_numpy()
```

We store the result into a dictionary `detect_res` with labels as *keys* and tuples containing coordinates of detected objects as *values*. 


**In particular, we need to turn the coordinates based on our cropped image to the coordinates based on our original image.**
  
```python
detect_res[robot[-1]].append((x1_,y1_,x2_,y2_))   # robot[-1]: the label
```
  
```python
for feature in feature_results:
    x11, y11, x22, y22 = feature[0], feature[1], feature[2], feature[3]
    detect_res[feature[-1]].append((math.floor(x1+x11), math.floor(y1+y11), math.ceil(x1+x22), math.ceil(y1+y22)))
```

E.G.
  
```python
> print(detect_res)
{robot:[(2,5,3,1),(3,9,1,6)],light:[(2,3,2,1)],armor:[(1,1,2,4)]}
```

In addition, during experiments we find some detected results with low confidences are generally useless. Hence, we do not store them in our `dect_res`.

```python
for robot in robot_results:
    if robot[-3] <= 0.8: continue   #robot[-3]: the confidence
             
    #further operations...
                       
    for feature in feature_results:
        if feature[-3] <= 0.6: continue
        
        #further operations...
```

</details>


<details close>
<summary> <b> 3D-Coordinate Computation </b> </summary>

In this part, we need to 

  
Randomly pick a point, suppose it exists in both the 1080\*1920-sized array and the 424\*512-sized array.


</details>


<details close>
<summary> <b> Send </b> </summary>


</details>

## Evaluation
To be continued...

## Future Work
To be continued...

## Acknowledgment
To be continued...
