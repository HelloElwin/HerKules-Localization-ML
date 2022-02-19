#include <libfreenect2/libfreenect2.hpp>
#include <libfreenect2/frame_listener_impl.h>
#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <std_msgs/Header.h>
#include <opencv2/opencv.hpp>
#include <iostream>

int main(int argc, char **argv)
{

	libfreenect2::Freenect2 freenect2;
	libfreenect2::Freenect2Device *device = 0;
	//libfreenect2::SyncMultiFrameListener *listenerColor, *listenerIrDepth;
	//libfreenect2::SyncMultiFrameListener *listener;
	
	ros::init(argc,argv,"c__grabbing");
	ros::NodeHandle nh;
	ros::Publisher colorpub;
	ros::Publisher depthpub;

	colorpub = nh.advertise<sensor_msgs::Image>("color",1);
	depthpub = nh.advertise<sensor_msgs::Image>("depth",1);

	cv_bridge::CvImage colormsg;
	cv_bridge::CvImage depthmsg;
	std_msgs::Header colorheader;
	std_msgs::Header depthheader;

	int num = freenect2.enumerateDevices();
	std::string serial = freenect2.getDefaultDeviceSerialNumber();
	device = freenect2.openDevice(serial);
	int types = 0;
	types |= libfreenect2::Frame::Color | libfreenect2::Frame::Ir | libfreenect2::Frame::Depth;
	libfreenect2::SyncMultiFrameListener listener(types);
//	listenerColor = new libfreenect2::SyncMultiFrameListener(libfreenect2::Frame::Color);
//	listenerIrDepth = new libfreenect2::SyncMultiFrameListener(libfreenect2::Frame::Ir | libfreenect2::Frame::Depth);
	libfreenect2::FrameMap frames;

	device->setColorFrameListener(&listener);
	device->setIrAndDepthFrameListener(&listener);
	device->start();

	ROS_INFO("%s","hihihi");
	while(true)
	{
		listener.waitForNewFrame(frames, 1000);
		colorheader.seq = 0;
		colorheader.stamp = ros::Time::now();


		libfreenect2::Frame *colorFrame = frames[libfreenect2::Frame::Color];

		depthheader.seq = 0;
		depthheader.stamp = ros::Time::now();
		libfreenect2::Frame *irFrame = frames[libfreenect2::Frame::Ir];
		libfreenect2::Frame *depthFrame = frames[libfreenect2::Frame::Depth];

		ROS_INFO("%s","finish receiving frames");
		cv::Mat color,depth;
//		cv::Mat(2,2,CV_8UC4,cv::Scalar(1, 2, 3, 4));
//		cv::Scalar(colorFrame->width);
//		cv::Scalar(colorFrame->data);
		ROS_INFO("%s","hahahahaha");
		cv::Mat(colorFrame->height,colorFrame->width,CV_8UC4,colorFrame->data).copyTo(color);
		//cv::Mat color = cv::Mat(colorFrame->height,colorFrame->width,CV_8UC4,colorFrame->data);
		//cv::Mat depth = cv::Mat(depthFrame->height,depthFrame->width,CV_32FC1,depthFrame->data);
		cv::Mat(depthFrame->height,depthFrame->width,CV_32FC1,depthFrame->data).copyTo(depth);
/*		cv::imshow("yywhaoshuai",color);
		cv::waitKey(0);
		cv::imshow("elwinhaoshuai",depth);
		cv::waitKey(0);*/

		colormsg.header = colorheader;
		colormsg.encoding = sensor_msgs::image_encodings::BGR8;
		colormsg.image = color;
		depthmsg.header = depthheader;
		depthmsg.encoding = sensor_msgs::image_encodings::TYPE_16UC1;
		depthmsg.image = depth;

		ROS_INFO("%s","finishing processing");
		colorpub.publish(colormsg.toImageMsg());
		depthpub.publish(depthmsg.toImageMsg());

//		listenerColor->release(frames);
//		listenerIrDepth->release(frames);
		listener.release(frames);

	}
	device->stop();
	device->close();
	return 0;
}
