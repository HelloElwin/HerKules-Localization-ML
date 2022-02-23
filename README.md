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


  ### color and depth image grabbing 
  <details open>
  <summary></summary>
  
  
  
  
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
