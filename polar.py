import numpy as np
import time
import cv2 as cv
import math
import pylibfreenect2 as plf

depth_q = 0.010000
color_q = 0.002199

h, w = np.mgrid[0:424, 0:512]

cameramatrix = np.load('cameramatrix.npy')
color_cx,color_cy,color_fx,color_fy,shift_m,shift_d,mx_x0y0,mx_x0y1,mx_x0y2,mx_x0y3,mx_x1y0,mx_x1y1,mx_x1y2,mx_x2y0,mx_x2y1,mx_x3y0,my_x0y0,my_x0y1,my_x0y2,my_x0y3,my_x1y0,my_x1y1,my_x1y2,my_x2y0,my_x2y1,my_x3y0,depth_cx,depth_cy,depth_fx,depth_fy,depth_k1,depth_k2,depth_k3,depth_p1,depth_p2 = cameramatrix

# print(color_cx, depth_fx)

def paint(pointlist):
    canvas = np.zeros((424, 512, 3))
    canvas = canvas + np.array([252,183,255])
    r_a = (218-33)/424
    g_a = (183-43)/424
    b_a = (255-255)/424
    for i in range(1, canvas.shape[0]):
        for j in range(canvas.shape[1]):
            canvas[i][j] = np.asarray([218,183,255])-np.asarray([int(r_a*i),int(g_a*i),int(b_a*i)])
    for pointlabel in pointlist:
        for pointindex in range(len(pointlist[pointlabel])):
            for point in pointlist[pointlabel][pointindex]:
                canvas[point//512][point%512] = np.asarray([64, 100, 160])
    return canvas[...,::-1]

def depth2color(x, y):

    x = (x - depth_cx) * depth_q
    y = (y - depth_cy) * depth_q

    wx = (x ** 2 * x * mx_x3y0) + (y ** 2 * y * mx_x0y3) + \
         (x ** 2 * y * mx_x2y1) + (y ** 2 * x * mx_x1y2) + \
         (x * x * mx_x2y0) + (y * y * mx_x0y2) + (x * y * mx_x1y1) + \
         (x * mx_x1y0) + (y * mx_x0y1) + (mx_x0y0)
    
    wy = (x ** 2 * x * my_x3y0) + (y ** 2 * y * my_x0y3) + \
         (x ** 2 * y * my_x2y1) + (y ** 2 * x * my_x1y2) + \
         (x * x * my_x2y0) + (y * y * my_x0y2) + (x * y * my_x1y1) + \
         (x * my_x1y0) + (y * my_x0y1) + (my_x0y0)

    rx = (wx / (color_fx * color_q)) - (shift_m / shift_d)
    ry = (wy / color_q) + color_cy

    return rx, ry

def distort(x, y):

    dx = (1.0 * x - depth_cx) / depth_fx
    dy = (1.0 * y - depth_cy) / depth_fy
    r2 = dx ** 2 + dy ** 2
    d2 = dx * dy * 2
    kr = 1 + ((depth_k3 * r2 + depth_k2) * r2 + depth_k1) * r2
    mx = depth_fx * (dx * kr + depth_p2 * (r2 + 2 * dx ** 2) + depth_p1 * d2) + depth_cx
    my = depth_fy * (dy * kr + depth_p1 * (r2 + 2 * dy ** 2) + depth_p2 * d2) + depth_cy

    return mx, my

def generate_map():

    map_x = np.zeros((424, 512))
    map_y = np.zeros((424, 512))
    map_i = np.zeros((424, 512))
    map_d = np.zeros((424, 512))
    
    for y in range(424):
        for x in range(512):
            mx, my = distort(x, y)
            rx, ry = depth2color(x, y)
            ix, iy = int(mx + 0.5), int(my + 0.5)
            if ix < 0 or ix >= 512 or iy < 0 or iy >= 424: index = -1
            else: index = iy * 512 + ix
            map_d[y][x] = index
            map_x[y][x] = rx
            map_y[y][x] = ry
            map_i[y][x] = int(ry + 0.5)

    return map_x, map_y, map_i, map_d

class Finder():

    #尝试不开相机，存储参数！

    def __init__(self):
        self.map_x, self.map_y, self.map_i, self.map_d = generate_map()
        self.map_d = self.map_d.flatten()

    def generate(self, depth):

        depth = depth.flatten()

        map_x, map_y, map_i, map_d = self.map_x, self.map_y, self.map_i, self.map_d

        depth = depth[map_d.astype(int)]
        map_c_off = (map_x + shift_m / depth.reshape((424, 512))) * color_fx + color_cx + map_i * 1920

        return map_c_off

    def findbbox(self, map_c_off, bboxes, depth):
        
        map_c_off = map_c_off.flatten()
        finalpoints = {}

#        for bbox in bboxes:
#            box = bbox[1]
#            m_x,m_y = (box[0] + box[2]) // 2,(box[1] + box[3]) // 2
#            m_index = m_y * 1920 + m_x
#            final_index = np.abs(map_c_off - m_index).argmin()
#            finalpoints.append((bbox[0], (final_index % 512, final_index // 512)))

        for bbox in bboxes:
            finalpoints[bbox] = []
            for box in bboxes[bbox]:
                m_x,m_y = (box[0] + box[2]) // 2,(box[1] + box[3]) // 2
                m_index = m_y * 1920 + m_x
                map_c_off[depth.flatten()==0] = np.inf
                final_index = np.abs(map_c_off - m_index).argmin()
                finalpoints[bbox].append((final_index % 512, final_index // 512))

        return finalpoints
    
    def depth2xyz_prepare(self, depth, candidate):
        xyz = {}
        for bbox in candidate:
            xyz[bbox] = []
            for subbox in candidate[bbox]:
                x, y, z = self.depth2xyz(depth, subbox[0], subbox[1])
                xyz[bbox].append((x, y, z))
        return xyz
                

    def depth2xyz(self, depth, x, y, depth_scale=1000):
        fx, fy = depth_fx, depth_fy
        cx, cy = depth_cx, depth_cy
        zz = depth[y][x]/depth_scale
        xx = (w[y][x] - cx) * zz / fx
        yy = (h[y][x] - cy) * zz / fy #顺序对吗？
        return xx, yy, zz
