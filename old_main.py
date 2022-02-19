import polar as plr
import numpy as np
import cv2 as cv
import detection
#import camera
import rospy
import time
import pylibfreenect2 as plf

def reduce2three(color):
    return color[:,:,:3]

def test_c_map(c_map, color):
    np.save('./test_map.npy', c_map)
    color = color.reshape(-1, 3)
    res = np.zeros((424, 512, 3))
    for i in range(424):
        for j in range(512):
            if c_map[i][j] < 0 or c_map[i][j] >= 1920 * 1080: continue
            res[i][j] = color[int(c_map[i][j])]
    np.save('color.npy', res)

def grab_from_camera():
    pass

if __name__ == '__main__':

    model = detection.Model()
    model.load()

    finder = plr.Finder()
    
    fn = plf.Freenect2()
    num_of_device = fn.enumerateDevices()
    serial = fn.getDefaultDeviceSerialNumber()
    device = fn.openDevice(serial)

    types = plf.FrameType.Color | plf.FrameType.Ir | plf.FrameType.Depth
    listener = plf.SyncMultiFrameListener(types)
    device.setColorFrameListener(listener)
    device.setIrAndDepthFrameListener(listener)

    device.start()

    while True:

        t00 = time.time()
        frames = plf.FrameMap()
        listener.waitForNewFrame(frames)

        color = frames[plf.FrameType.Color]
        depth = frames[plf.FrameType.Depth]
        infrared = frames[plf.FrameType.Ir]


        color = color.asarray(dtype=np.uint8)[:,:,:3]
#        cv.imwrite("./a.jpg", color)
        depth = depth.asarray(dtype=np.float32)

 #       print(color.shape, depth.shape)

        t0 = time.time()
        print(f"===finished grabbing, time={t0-t00}")

        c_map = finder.generate(depth)
        t1 = time.time()
        print(f"===finished mapping, time={t1-t0}")

        test_c_map(c_map, color)
        np.save('depth.npy', depth)

        bboxes = model.inference(color)
        t2 = time.time()
        print(f"===finished inferencing, time={t2-t1}")
        print("boxes", bboxes)

        candidates = finder.findbbox(c_map, bboxes, depth)
        t3 = time.time()
        print(f"===finished candidates, time={t3-t2}")
        print("cans:", candidates)

        print(f"===finished one frame, time={time.time()-t00}")

        listener.release(frames)

#        test_can = []

#        for bbox in candidates:
#            for idx, subbox in enumerate(candidates[bbox]):
#                print("##########", depth[candidates[bbox][idx][1]][candidates[bbox][idx][0]])
#                x, y, z = finder.depth2xyz(depth, candidates[bbox][idx][0], candidates[bbox][idx][1]) #之后不要只传如一个点
#                test_can.append([x, y, z])
#                print("===", bbox, f"({x:.3f}, {y:.3f}, {z:.3f}")

#        np.save('./can.npy', test_can)
