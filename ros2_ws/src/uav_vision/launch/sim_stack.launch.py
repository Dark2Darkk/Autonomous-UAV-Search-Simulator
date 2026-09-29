import os

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    ExecuteProcess,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


WORLD = 'urban_search'


def generate_launch_description():

    uav_share = get_package_share_directory('uav_vision')

    # --------------------------------------------------
    # Config / launch paths
    # --------------------------------------------------

    slam_config = os.path.join(
        uav_share,
        'config',
        'slam.yaml'
    )

    slam_launch = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    nav_launch = os.path.join(
        uav_share,
        'launch',
        'uav_nav.launch.py'
    )

    # --------------------------------------------------
    # Gazebo topic names
    # --------------------------------------------------

    lidar_topic = (
        f'/world/{WORLD}/model/x500_lidar_cam_0/'
        'link/link/sensor/lidar_2d_v2/scan'
    )

    camera_topic = (
        f'/world/{WORLD}/model/x500_lidar_cam_0/'
        'link/camera_link/sensor/camera/image'
    )

    # --------------------------------------------------
    # PX4 <-> ROS 2 DDS agent
    # --------------------------------------------------

    microxrce_agent = ExecuteProcess(
        cmd=[
            'MicroXRCEAgent',
            'udp4',
            '-p',
            '8888'
        ],
        output='screen'
    )

    # --------------------------------------------------
    # Gazebo -> ROS 2 bridges
    # --------------------------------------------------

    bridges = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',

        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',

            lidar_topic
            + '@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',

            camera_topic
            + '@sensor_msgs/msg/Image[gz.msgs.Image',

            '/model/x500_lidar_cam_0/odometry'
            '@nav_msgs/msg/Odometry[gz.msgs.Odometry',

            '/model/x500_lidar_cam_0/pose'
            '@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],

        remappings=[
            (
                lidar_topic,
                '/uav/lidar/scan'
            ),

            (
                camera_topic,
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

    # --------------------------------------------------
    # base_link -> lidar frame
    # --------------------------------------------------

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

    # --------------------------------------------------
    # SLAM Toolbox
    # --------------------------------------------------

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            slam_launch
        ),

        launch_arguments={
            'slam_params_file': slam_config,
            'use_sim_time': 'true',
        }.items()
    )

    # --------------------------------------------------
    # RViz
    # --------------------------------------------------

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        parameters=[
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # --------------------------------------------------
    # Nav2
    #
    # Give bridges + SLAM time to establish TF/map first.
    # --------------------------------------------------

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            nav_launch
        )
    )

    delayed_nav2 = TimerAction(
        period=5.0,
        actions=[
            nav2
        ]
    )

    return LaunchDescription([
        microxrce_agent,
        bridges,
        lidar_tf,
        slam,
        rviz,
        delayed_nav2,
    ])