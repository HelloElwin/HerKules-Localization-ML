# HerKules-Localization-ML
This Github repository demonstrate the ML-based localization method for RoboMaster-AI.


Our idea is to find (if could) the ***the nearest points to the centers*** of the robot itself and its feature elements. Original results are indexes of the points in the 1080\*1920-sized color-image numpy array. We then calculate the corresponding indexes of these points in the 424\*512-sized depth-image numpy array. The final results are generated with these corresponding indexes together with our depth-image map.


This method includes ROS publish and subscription, callback function, yolov5, opencv, open3d, etc..




## Method
Our localization pipeline consists of 5 parts:


* Grabbing color and depth images.
* Detecting robots in the color image.
* Detecting robot armors in the detected bounding boxes of robots.
* Computing 3D coordinates of the armors with the depth image.
* Sending out the coordinates.


Now we would like to tell more details by parts.


***

  
### color and depth image grabbing 
<details open>
<summary>(click to view details)</summary>

To achieve a high-speed grabbing, we use **ros subscriber** to receive real-time depth and color image from Kinect2 and send the received images to two callback functions. In the callback functions, we translate the depth and color image data to depth and color numpy array respectively before our further detection and calculation.
<br />
<br />
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

Since numpy is famous for its high speed with calculations related to matrixes, we translate the sensor message Image to one-dimension numpy array in callback function.

```python
depth = np.frombuffer(depth_msg.data, dtype=np.float32).reshape(424, 512)
color = np.frombuffer(color_msg.data, dtype=np.uint8).reshape(1080, 1920, 4)
```
  
To guarantee that the depth image and the color image we are dealing with are grabbed from the same time, we set two bool variables to indicate whether we have finished progressing the last frame and are able to progress the next one. The original value of these two variables are True. When we received one depth image, we translate the sensor message to numpy array and save it in `depth` before we set the `depth_flag` to False. The same is applied to `color_flag`.
  

After we finished progressing a frame, we set `depth_flag` and `color_flag` back to True.
  
```python
if depth_flag == True:
    depth = np.frombuffer(depth_msg.data, dtype=np.float32).reshape(424, 512)
    depth_flag = False
```

```python
if color_flag == True:
    color_flag = False
    color = np.frombuffer(color_msg.data, dtype=np.uint8).reshape(1080, 1920, 4)

    # further operations

    color_flag = True
    depth_flag = True
```

</details>


### robot detection
<details open>
<summary></summary>



</details>


### armor detection
<details open>
<summary></summary>



</details>


### 3D coordinates computation
<details open>
<summary></summary>



</details>


### send
<details open>
<summary></summary>



</details>

## Evaluation
To be continued...

## Future Work
To be continued...

## Acknowledgment
To be continued...
