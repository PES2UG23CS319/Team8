cmake_minimum_required(VERSION 3.8)
project(ball_tracker)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)

# Install Python nodes
ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  ball_tracker/perception_node.py
  ball_tracker/control_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch, description, worlds
install(DIRECTORY
  launch
  description
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
