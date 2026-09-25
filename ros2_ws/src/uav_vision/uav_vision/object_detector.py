import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO

class ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector')

        self.bridge = CvBridge()

        self.model = YOLO('yolo26n.pt')

        self.subscription = self.create_subscription(Image, '/uav/camera/image_raw', self.image_callback, 10)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model.predict(frame, classes=[0], conf=0.5, verbose=False)

        boxes = results[0].boxes

        if len(boxes) > 0:
            for box in boxes:
                confidence = float(box.conf[0])
                x, y, width, height = box.xywh[0].tolist()
                self.get_logger().info(
                    f'Person Detected | '
                    f'Confidence: {confidence:.2f} | '
                    f'Center: ({x:.0f}, {y:.0f}) | '
                    f'Size: {width:.0f}x{height:.0f}'
                )


def main(args=None):
    rclpy.init(args=args)

    node = ObjectDetector()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()