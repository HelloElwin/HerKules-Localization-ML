#include <libfreenect2/libfreenect2.hpp>
#include <libfreenect2/frame_listener_impl.h>
#include <ros/ros.h>
#include <sensor_msgs/Image.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <std_msgs/Header.h>
#include <opencv2/opencv.hpp>

int main(int argc, char **argv)
{

	libfreenect2::Freenect2 freenect2;
	libfreenect2::Freenect2Device *device = 0;
	ros::init(argc,argv,"c__grabbing");
	ros::NodeHandle nh;
	ros::Publisher colorpub;
	ros::Publisher depthpub;

	colorpub = nh.advertise<sensor_msgs::Image>("color",100);
	depthpub = nh.advertise<sensor_msgs::Image>("depth",100);

	cv_bridge::CvImage colormsg;
	cv_bridge::CvImage depthmsg;
	std_msgs::Header colorheader;
	std_msgs::Header depthheader;

	int num = freenect2.enumerateDevices();
	std::string serial = freenect2.getDufaultDevuceSerialNumber();
	device = freenect2.openDevice(serial);
	int types = 0;
	types |= libfreenect2::Frame::Color | libfreenect2::Frame::Ir | libfreenect2::Frame::Depth;
	libfreenect2::SyncMultiFrameListener listener(types);
	libfreenect2::FrameMap frames;

	device->setColorFrameListener(&listener);
	device->setIrAndDepthFrameListener(&listener);
	device->start();

	while True
	{
		colorheader.seq = counter;
		colorheader.stamp = ros::Time::now();
		libfreenect2::Frame *colorFrame = frames[libfreenect2::Frame::Color];

		depthheader.seq = counter;
		depthheader.stamp = ros::Time::now();
		libfreenect2::Frame *irFrame = frames[libfreenect2::Frame::Ir];
		libfreenect2::Frame *depthFrame = frames[libfreenect2::Frame::Depth];

		libfreenect2::Frame color;
		libfreenect2::Frame depth;
		cv::Mat color = cv::Mat(colorFrame->height,colorFrame->width,CV_8UC4,colorFrame->data);
		cv::Mat depth = cv::Mat(depthFrame->height,depthFrame->width,CV_32FC1,depthorame->data);

		colormsg.header = colorheader;
		colormsg.encoding = sensor_msgs::image_encodings::BGR8;
		colormsg.image = color;
		depthmsg.header = depthheader;
		depthmsg.encoding = sensor_msgs::image_encodings::TYPE_16UC1;
		depthmsg.image = depth;

		colorpub.publish(colormsg.toImageMsg());
		depthpub.publish(depthmsg.toImageMsg());

		listener.release(frames);

	}
	device->stop();
	device->close();
	return 0;
}
