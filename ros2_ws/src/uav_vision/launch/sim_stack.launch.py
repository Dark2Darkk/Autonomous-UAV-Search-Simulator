import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    slam_config = os.path.expanduser(
        '~/ros2_ws/src/uav_vision/config/slam.yaml'
    )

    slam_launch = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    bridges = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',

        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',

            '/world/walls/model/x500_lidar_cam_0/link/link/sensor/lidar_2d_v2/scan'
            '@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',

            '/world/walls/model/x500_lidar_cam_0/link/camera_link/sensor/camera/image'
            '@sensor_msgs/msg/Image[gz.msgs.Image',

            '/model/x500_lidar_cam_0/odometry'
            '@nav_msgs/msg/Odometry[gz.msgs.Odometry',

            '/model/x500_lidar_cam_0/pose'
            '@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],

        remappings=[
            (
                '/world/walls/model/x500_lidar_cam_0/link/link/sensor/lidar_2d_v2/scan',
                '/uav/lidar/scan'
            ),

            (
                '/world/walls/model/x500_lidar_cam_0/link/camera_link/sensor/camera/image',
                '/uav/camera/image_raw'
            ),

            (
                '/model/x500_lidar_cam_0/odometry',
                '/uav/odom'
            ),

            (
                '/model/x500_lidar_cam_0/pose',
                '/tf'
            ),
        ],
    )

    lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0.12',
            '--y', '0.0',
            '--z', '0.26',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'link',
        ],
        output='screen'
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch),
        launch_arguments={
            'slam_params_file': slam_config,
            'use_sim_time': 'true',
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        parameters=[
            {'use_sim_time': True}
        ],
        output='screen'
    )

    return LaunchDescription([
        bridges,
        lidar_tf,
        slam,
        rviz,
    ])
