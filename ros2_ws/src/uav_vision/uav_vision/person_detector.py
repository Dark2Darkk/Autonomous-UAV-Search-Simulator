import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from cv_bridge import CvBridge, CvBridgeError

from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy
)

from ultralytics import YOLO


class ObjectDetector(Node):

    def __init__(self):
        super().__init__('object_detector')

        self.bridge = CvBridge()

        # Load YOLO model
        self.model = YOLO('yolo26n.pt')

        # Keep only the newest camera frame and use
        # sensor-compatible BEST_EFFORT QoS.
        camera_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )

        self.subscription = self.create_subscription(
            Image,
            '/uav/camera/image_raw',
            self.image_callback,
            camera_qos
        )

        self.confidence_pub = self.create_publisher(
            Float32,
            '/uav/person_confidence',
            10
        )

        self.get_logger().info('Person detector started')

    def image_callback(self, msg):

        # Convert ROS Image -> OpenCV image
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

        except CvBridgeError as error:
            self.get_logger().error(
                f'Failed to convert camera image: {error}'
            )
            return

        # Run YOLO.
        #
        # classes=[0] means only look for COCO "person".
        # conf=0.80 means detections below 80% are discarded.
        results = self.model.predict(
            frame,
            verbose=False,
            classes=[0],
            conf=0.80
        )

        best_confidence = 0.0

        # Find the highest-confidence person detection
        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                confidence = float(box.conf[0])

                best_confidence = max(
                    best_confidence,
                    confidence
                )

        # Publish confidence to mission controller.
        #
        # 0.0 means no valid person detection this frame.
        message = Float32()
        message.data = best_confidence

        self.confidence_pub.publish(message)



def main(args=None):

    rclpy.init(args=args)

    node = ObjectDetector()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()