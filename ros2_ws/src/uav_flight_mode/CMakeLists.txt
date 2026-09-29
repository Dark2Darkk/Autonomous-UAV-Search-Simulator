cmake_minimum_required(VERSION 3.8)
project(uav_flight_mode)

if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(eigen3_cmake_module REQUIRED)
find_package(Eigen3 REQUIRED)

find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(px4_msgs REQUIRED)
find_package(px4_ros2_cpp REQUIRED)

include_directories(
    include
    ${Eigen3_INCLUDE_DIRS}
)

add_executable(
    nav2_flight_mode
    src/main.cpp
)

ament_target_dependencies(
    nav2_flight_mode
    rclcpp
    geometry_msgs
    px4_msgs
)

target_link_libraries(
    nav2_flight_mode
    Eigen3::Eigen
    px4_ros2_cpp::px4_ros2_cpp
)

install(
    TARGETS nav2_flight_mode
    DESTINATION lib/${PROJECT_NAME}
)

ament_package()