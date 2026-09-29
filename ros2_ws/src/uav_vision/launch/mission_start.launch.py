import os

from launch import LaunchDescription
from launch.actions import TimerAction

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    explore_config = os.path.join(
        get_package_share_directory('uav_vision'),
        'config',
        'explore.yaml'
    )

    # PX4 ROS 2 external flight mode:
    # preflight -> arm -> takeoff -> Nav2 flight mode
    flight_mode = Node(
        package='uav_flight_mode',
        executable='nav2_flight_mode',
        name='uav_flight_mode',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ]
    )

    venv_path = os.environ.get('VIRTUAL_ENV')

    if not venv_path:
        raise RuntimeError(
            'Virtual environment is not active. '
            'Run: source .venv/bin/activate'
        )

    venv_site_packages = os.path.join(
        venv_path,
        'lib',
        'python3.12',
        'site-packages'
    )
    # YOLO person detector
    person_detector = Node(
        package='uav_vision',
        executable='person_detector',
        name='person_detector',
        output='screen',

        additional_env={
            'PYTHONPATH':
                venv_site_packages
                + ':'
                + os.environ.get('PYTHONPATH', '')
        }
    )

    # Mission logic:
    # person found -> stop exploration -> report coordinates
    mission_controller = Node(
        package='uav_vision',
        executable='mission_controller',
        name='mission_controller',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ]
    )

    # Frontier exploration
    explore = Node(
        package='explore_lite',
        executable='explore',
        name='explore_node',
        output='screen',
        parameters=[
            explore_config
        ]
    )

    # Temporary delay so PX4 can finish takeoff and enter
    # our Nav2 flight mode before explore_lite sends goals.
    delayed_explore = TimerAction(
        period=15.0,
        actions=[
            explore
        ]
    )

    return LaunchDescription([
        flight_mode,
        person_detector,
        mission_controller,
        delayed_explore,
    ])