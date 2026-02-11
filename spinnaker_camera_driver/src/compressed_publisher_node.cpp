#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <image_transport/image_transport.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

namespace spinnaker_camera_driver
{
class ImageProcessorNode : public rclcpp::Node
{
public:
  ImageProcessorNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions())
  : rclcpp::Node("image_processor", options)
  {
    // Declare parameters
    this->declare_parameter<int>("resize_width", 640);
    this->declare_parameter<int>("resize_height", 480);
    this->declare_parameter<int>("jpeg_quality", 80);

    int width = this->get_parameter("resize_width").as_int();
    int height = this->get_parameter("resize_height").as_int();

    // Create image transport
    image_transport::ImageTransport it(this);

    // Subscriber using image_transport for efficient transport
    sub_ = it.subscribe("image_raw", 10, std::bind(&ImageProcessorNode::imageCallback, this, std::placeholders::_1));

    // Publisher for processed image
    pub_ = it.advertise("image_compressed", 10);

    RCLCPP_INFO(this->get_logger(), "Image Processor Node started");
  }

private:
  void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr & msg)
  {
    try {
      // Convert ROS image to OpenCV Mat
      cv_bridge::CvImageConstPtr cv_ptr = cv_bridge::toCvShare(msg, "bgr8");

      // Get parameters
      int target_width = this->get_parameter("resize_width").as_int();
      int target_height = this->get_parameter("resize_height").as_int();
      int jpeg_quality = this->get_parameter("jpeg_quality").as_int();

      // Resize image
      cv::Mat resized;
      cv::resize(cv_ptr->image, resized, cv::Size(target_width, target_height));

      // Compress with JPEG (optional compression)
      std::vector<int> compression_params = {cv::IMWRITE_JPEG_QUALITY, jpeg_quality};
      std::vector<uchar> buffer;
      cv::imencode(".jpg", resized, buffer, compression_params);

      // Decode back to Mat for publishing
      cv::Mat compressed = cv::imdecode(buffer, cv::IMREAD_COLOR);

      // Convert back to ROS message
      cv_bridge::CvImage cv_image;
      cv_image.header = msg->header;
      cv_image.encoding = "bgr8";
      cv_image.image = compressed;

      pub_.publish(cv_image.toImageMsg());

    } catch (cv_bridge::Exception & e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
    }
  }

  image_transport::Subscriber sub_;
  image_transport::Publisher pub_;
};

}  // namespace spinnaker_camera_driver

#include <rclcpp_components/register_node_macro.hpp>
RCLCPP_COMPONENTS_REGISTER_NODE(spinnaker_camera_driver::ImageProcessorNode)