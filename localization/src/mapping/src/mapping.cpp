#include <iostream>
#include <cstdio>
#include <ros/ros.h>
#include "std_msgs/Float32MultiArray.h"
#include "std_msgs/UInt8MultiArray.h"

using namespace std;

float color_cx,color_cy,color_fx,color_fy,shift_m,shift_d,mx_x0y0,mx_x0y1,mx_x0y2,mx_x0y3,mx_x1y0,mx_x1y1,mx_x1y2,mx_x2y0,mx_x2y1,mx_x3y0,my_x0y0,my_x0y1,my_x0y2,my_x0y3,my_x1y0,my_x1y1,my_x1y2,my_x2y0,my_x2y1,my_x3y0,depth_cx,depth_cy,depth_fx,depth_fy,depth_k1,depth_k2,depth_k3,depth_p1,depth_p2;

int distort_map[512*424];
float depth2color_mapx[512*424];
float depth2color_mapy[512*424];
int depth2color_mapyi[512*424];
static const float depth_q = 0.010000;
static const float color_q = 0.002199;
const int size_depth = 512 * 424;
const int size_color = 1920 * 1080;
int *map_dist = distort_map;
float *mapx = depth2color_mapx;
float *mapy = depth2color_mapy;
int *mapyi = depth2color_mapyi;
int map_c_off_data[512*424];

void get_camera_params() {
	freopen("./cameramatrix.txt", "r", stdin);
	scanf("%f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f",&color_cx,&color_cy,&color_fx,&color_fy,&shift_m,&shift_d,&mx_x0y0,&mx_x0y1,&mx_x0y2,&mx_x0y3,&mx_x1y0,&mx_x1y1,&mx_x1y2,&mx_x2y0,&mx_x2y1,&mx_x3y0,&my_x0y0,&my_x0y1,&my_x0y2,&my_x0y3,&my_x1y0,&my_x1y1,&my_x1y2,&my_x2y0,&my_x2y1,&my_x3y0,&depth_cx,&depth_cy,&depth_fx,&depth_fy,&depth_k1,&depth_k2,&depth_k3,&depth_p1,&depth_p2);
	fclose(stdin);
}

void depth2color(float mx, float my, float &rx, float &ry)
{
	mx = (mx - depth_cx) * depth_q;
	my = (my - depth_cy) * depth_q;
	
	float wx = (mx * mx * mx * mx_x3y0) + (my * my * my * mx_x0y3) +
    (mx * mx * my * mx_x2y1) + (my * my * mx * mx_x1y2) +
    (mx * mx * mx_x2y0) + (my * my * mx_x0y2) + (mx * my * mx_x1y1) +
    (mx * mx_x1y0) + (my * mx_x0y1) + (mx_x0y0);
	
	float wy = (mx * mx * mx * my_x3y0) + (my * my * my * my_x0y3) +
    (mx * mx * my * my_x2y1) + (my * my * mx * my_x1y2) +
    (mx * mx * my_x2y0) + (my * my * my_x0y2) + (mx * my * my_x1y1) +
    (mx * my_x1y0) + (my * my_x0y1) + (my_x0y0);

	rx = (wx / (color_fx * color_q)) - shift_m / shift_d;
	ry = wy / color_q +color_cy;
}

void distort(int mx, int my, float &x, float &y)
{
	float dx = ((float)mx - depth_cx) / depth_fx;
	float dy = ((float)my - depth_cy) / depth_fy;
	float d2 = dx * dx;
	float r2 = dx * dx + dy * dy;
	float kr = 1 + ((depth_k3 * r2 + depth_k2) * r2 + depth_k1) * r2;
	x = depth_fx * (dx * kr + depth_p2 * (r2 + 2 * dx * dx) + depth_p1 * dx * dy * 2) + depth_cx;
	y = depth_fy * (dy * kr + depth_p1 * (r2 + 2 * dy * dy) + depth_p2 * dx * dy * 2) + depth_cy;
}

void prepare_map() {
	float mx, my;
	int ix, iy, index;
	float rx, ry;
	for (int y = 0; y < 424; y++) 
	{
		for (int x = 0; x < 512; x++) 
		{
			distort(x,y,mx,my);
			ix = (int)(mx + 0.5f);
			iy = (int)(my + 0.5f);
			if (ix < 0 || ix >= 512 || iy < 0 || iy >= 424)
				index = -1;
			else
				index = iy * 512 + ix;
			*map_dist++ = index;

			depth2color(x,y,rx,ry);
			*mapx++ = rx;
			*mapy++ = ry;
			*mapyi++ = (int)(ry + 0.5f);
		}
	}
}
class Mapper {

	public:

		ros::Publisher pub;
		ros::Subscriber sub;
		ros::NodeHandle nh;
		void init()
		{
			pub = nh.advertise<std_msgs::UInt8MultiArray>("/loc_c_map", 10);
			sub = nh.subscribe("/loc_depth", 1,&Mapper::generate_c_map,this);
			//sub = nh.subscribe<std_msgs::Float32MultiArray>("/loc_depth", 10, boost::bind(&generate_c_map,_2,&pub));
		}

	private:

		void publish_msg(int msg[512 * 424])
		{
			std_msgs::UInt8MultiArray msg_map_c;
			copy(msg, msg + 512 * 424, back_inserter(msg_map_c.data));
			pub.publish(msg_map_c);
			ROS_INFO("%s","wawawawawa");
		}

		void generate_c_map(const std_msgs::Float32MultiArray depth_data) 
		//static void generate_c_map(const std_msgs::Float32MultiArray depth_data,ros::Publisher *pub) 
		{
			ROS_INFO("%s","for time");
			int* map_c_off = map_c_off_data;
			float uuxuu = 0;
			/*for(int i = 100000; i <= 100100; i++)
			{
				ROS_INFO("%f",depth_data.data[i]);
			}*/
			for(int i = 0;i<512*424;i++)
			{
				uuxuu += depth_data.data[i];
			}
			ROS_INFO("=====%f", uuxuu);
			map_dist = distort_map;
			mapx = depth2color_mapx;
			mapy = depth2color_mapy;
			mapyi = depth2color_mapyi;
			for(int i = 0; i < size_depth; i++, ++map_dist, ++mapx, ++mapyi, ++map_c_off) 
			{
				const int index = *map_dist;
				if(index < 0)
				{
					*map_c_off = -1;
					continue;
				}

				const float z = depth_data.data[index];

				if(z <= 0.0f)
				{
					*map_c_off = -1;
					continue;
				}

				const float rx = (*mapx + (shift_m / z)) * color_fx + color_cx;
				const int cx = int(rx+0.5); 
				const int cy = *mapyi;
				const int c_off = cx + cy * 1920;

				if(c_off < 0 || c_off >= size_color)
				{
					*map_c_off = -1;
					continue;
				}

				*map_c_off = c_off;
			}
			ROS_INFO("%s", "Ready to publish");
			for(int i = 1;i<=100;i++)
			{
				ROS_INFO("%d",map_c_off[i]);
			}
			publish_msg(map_c_off_data);
			/*std_msgs::UInt8MultiArray msg_map_c;
			copy(map_c_off_data, map_c_off_data + 512 * 424, back_inserter(msg_map_c.data));
			pub.publish(msg_map_c);*/
		}
};

int main(int argc, char **argv) {

	get_camera_params();
	prepare_map();

	ros::init(argc, argv, "loc_c_mapper");
	ROS_INFO("%s", "Finished initialization");

	Mapper mapper;
	ROS_INFO("%s", "Created mapper");
	mapper.init();
	ros::spin();

	return 0;
}
