import math

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy,
    HistoryPolicy,
)

from geometry_msgs.msg import Twist

from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
)


class Nav2PX4Adapter(Node):

    def __init__(self):
        super().__init__('nav2_px4_adapter')

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # Nav2 command
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10,
        )

        # PX4 state
        self.local_position_sub = self.create_subscription(
            VehicleLocalPosition,
            '/fmu/out/vehicle_local_position_v1',
            self.local_position_callback,
            px4_qos,
        )

        # PX4 commands
        self.offboard_pub = self.create_publisher(
            OffboardControlMode,
            '/fmu/in/offboard_control_mode',
            px4_qos,
        )

        self.trajectory_pub = self.create_publisher(
            TrajectorySetpoint,
            '/fmu/in/trajectory_setpoint',
            px4_qos,
        )

        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand,
            '/fmu/in/vehicle_command',
            px4_qos,
        )

        self.forward_velocity = 0.0
        self.yaw_rate = 0.0

        self.heading = 0.0
        self.heading_valid = False

        self.last_cmd_time = None

        self.offboard_counter = 0
        self.offboard_requested = False

        # 10 Hz
        self.timer = self.create_timer(0.1, self.timer_callback)

    def cmd_vel_callback(self, msg):
        self.forward_velocity = msg.linear.x
        self.yaw_rate = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def local_position_callback(self, msg):
        self.heading = msg.heading
        self.heading_valid = msg.heading_good_for_control

    def timer_callback(self):
        self.publish_offboard_heartbeat()

        if not self.heading_valid:
            return

        # Stop if Nav2 commands disappear
        if self.last_cmd_time is None:
            forward = 0.0
            yaw_rate = 0.0
        else:
            age = (
                self.get_clock().now() - self.last_cmd_time
            ).nanoseconds / 1e9

            if age > 0.5:
                forward = 0.0
                yaw_rate = 0.0
            else:
                forward = self.forward_velocity
                yaw_rate = self.yaw_rate

        # Nav2 body-forward velocity -> PX4 NED world velocity
        velocity_north = forward * math.cos(self.heading)
        velocity_east = forward * math.sin(self.heading)

        self.publish_velocity_setpoint(
            velocity_north,
            velocity_east,
            yaw_rate,
        )

        # Give PX4 1 second of heartbeat/setpoints first
        if self.offboard_counter < 10:
            self.offboard_counter += 1

        elif not self.offboard_requested:
            self.engage_offboard_mode()
            self.offboard_requested = True

    def publish_offboard_heartbeat(self):
        msg = OffboardControlMode()

        msg.position = False
        msg.velocity = True
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.thrust_and_torque = False
        msg.direct_actuator = False

        msg.timestamp = self.timestamp_us()

        self.offboard_pub.publish(msg)

    def publish_velocity_setpoint(
        self,
        velocity_north,
        velocity_east,
        ros_yaw_rate,
    ):
        msg = TrajectorySetpoint()

        nan = float('nan')

        # Velocity control only
        msg.position = [nan, nan, nan]

        msg.velocity = [
            float(velocity_north),
            float(velocity_east),
            0.0,
        ]

        msg.acceleration = [nan, nan, nan]
        msg.jerk = [nan, nan, nan]

        msg.yaw = nan

        # ROS +Z yaw is opposite PX4 NED +Z yaw
        msg.yawspeed = float(-ros_yaw_rate)

        msg.timestamp = self.timestamp_us()

        self.trajectory_pub.publish(msg)

    def engage_offboard_mode(self):
        msg = VehicleCommand()

        msg.command = VehicleCommand.VEHICLE_CMD_DO_SET_MODE

        msg.param1 = 1.0
        msg.param2 = 6.0

        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True

        msg.timestamp = self.timestamp_us()

        self.vehicle_command_pub.publish(msg)

        self.get_logger().info('Requested PX4 Offboard mode')

    def timestamp_us(self):
        return int(self.get_clock().now().nanoseconds / 1000)


def main(args=None):
    rclpy.init(args=args)

    node = Nav2PX4Adapter()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
