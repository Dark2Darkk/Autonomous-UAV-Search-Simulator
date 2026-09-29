import rclpy
from rclpy.node import Node
from rclpy.time import Time

from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import PoseStamped

from tf2_ros import Buffer, TransformListener, TransformException


class MissionController(Node):

    def __init__(self):
        super().__init__('mission_controller')

        self.confidence_threshold = 0.80


        self.detection_confirmed = False
        self.person_found = False

        # --------------------------------------------------
        # Subscriptions
        # --------------------------------------------------

        self.confidence_sub = self.create_subscription(
            Float32,
            '/uav/person_confidence',
            self.confidence_callback,
            10
        )

        # --------------------------------------------------
        # Publishers
        # --------------------------------------------------

        # explore_lite:
        # True  = resume
        # False = stop
        self.explore_pub = self.create_publisher(
            Bool,
            '/explore/resume',
            10
        )

        self.target_pub = self.create_publisher(
            PoseStamped,
            '/uav/target_report',
            10
        )

        # --------------------------------------------------
        # TF
        # --------------------------------------------------

        self.tf_buffer = Buffer()

        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

        # Used only after a detection has been confirmed.
        # Keeps retrying position lookup until TF is available.
        self.report_timer = self.create_timer(
            0.2,
            self.report_timer_callback
        )

        self.get_logger().info(
            'Mission controller started'
        )

    # --------------------------------------------------
    # Detection logic
    # --------------------------------------------------

    def confidence_callback(self, msg):

        if self.detection_confirmed:
            return

        confidence = msg.data

        if confidence >= self.confidence_threshold:

            self.get_logger().info(
                f'Person detected with confidence: {confidence:.2f}'
            )

            self.confirm_detection()

    # --------------------------------------------------
    # Detection confirmed
    # --------------------------------------------------

    def confirm_detection(self):

        if self.detection_confirmed:
            return

        self.detection_confirmed = True

        self.get_logger().info(
            'Person detection confirmed'
        )

        # Stop explore_lite.
        pause_message = Bool()
        pause_message.data = False

        self.explore_pub.publish(
            pause_message
        )

        self.get_logger().info(
            'Exploration stop requested'
        )

    # --------------------------------------------------
    # Position reporting
    # --------------------------------------------------

    def report_timer_callback(self):

        if not self.detection_confirmed:
            return

        if self.person_found:
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                'map',
                'base_link',
                Time()
            )

        except TransformException as error:

            self.get_logger().warn(
                f'Waiting for detection position TF: {error}',
                throttle_duration_sec=2.0
            )

            return

        target = PoseStamped()

        target.header.stamp = (
            self.get_clock().now().to_msg()
        )

        target.header.frame_id = 'map'

        target.pose.position.x = (
            transform.transform.translation.x
        )

        target.pose.position.y = (
            transform.transform.translation.y
        )

        target.pose.position.z = (
            transform.transform.translation.z
        )

        target.pose.orientation = (
            transform.transform.rotation
        )

        self.target_pub.publish(
            target
        )

        self.person_found = True

        self.get_logger().info(
            'PERSON FOUND'
        )

        self.get_logger().info(
            'DETECTION LOCATION '
            f'x={target.pose.position.x:.2f}, '
            f'y={target.pose.position.y:.2f}, '
            f'z={target.pose.position.z:.2f}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = MissionController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()