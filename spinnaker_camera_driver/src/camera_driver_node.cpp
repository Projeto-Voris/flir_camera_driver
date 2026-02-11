// -*-c++-*--------------------------------------------------------------------
// Copyright 2023 Bernd Pfrommer <bernd.pfrommer@gmail.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/multi_threaded_executor.hpp>
#include <spinnaker_camera_driver/camera_driver.hpp>
// include the image processor component's header (create if missing)
#include <spinnaker_camera_driver/compressed_publisher_node.hpp>

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  auto opts = rclcpp::NodeOptions().use_intra_process_comms(true);

  // camera driver node (lifecycle/composable)
  auto camera_node = std::make_shared<spinnaker_camera_driver::CameraDriver>(opts);

  // image processor node (compressed publisher)
  auto image_node = std::make_shared<spinnaker_camera_driver::ImageProcessorNode>(opts);

  RCLCPP_INFO(camera_node->get_logger(), "camera driver and image processor starting in same process");

  rclcpp::executors::MultiThreadedExecutor exec;
  // add node base interfaces so lifecycle nodes/components are accepted
  exec.add_node(camera_node->get_node_base_interface());
  exec.add_node(image_node->get_node_base_interface());

  exec.spin();

  exec.remove_node(image_node->get_node_base_interface());
  exec.remove_node(camera_node->get_node_base_interface());

  image_node.reset();
  camera_node.reset();

  rclcpp::shutdown();
  return 0;
}
