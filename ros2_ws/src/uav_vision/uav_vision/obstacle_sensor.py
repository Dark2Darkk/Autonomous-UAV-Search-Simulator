import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data



class ObstacleSensor(Node):

    def __init__(self):
        super().__init__('obstacle_sensor')

        self.subscription = self.create_subscription(LaserScan, '/uav/lidar/scan', self.scan_callback, qos_profile_sensor_data)

    
    def scan_callback(self, msg):
        ranges = msg.ranges

        valid_ranges = [
            distance for distance in ranges
            if math.isfinite(distance)
            and distance >= msg.range_min
            and distance <= msg.range_max
        ]

        if len(valid_ranges) == 0:
            return

        closest = min(valid_ranges)

        self.get_logger().info(f'Closest obstacle: {closest:.2f} m')



def main(args=None):
    rclpy.init(args=args)

    node = ObstacleSensor()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()