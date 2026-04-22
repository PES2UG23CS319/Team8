#!/usr/bin/env python3
"""
perception_node.py
Shows detection using OpenCV window + publishes detection
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np


# ── HSV colour ranges ─────────────────────────────────────────────

RED_LOWER1  = np.array([0,   120,  70])
RED_UPPER1  = np.array([10,  255, 255])
RED_LOWER2  = np.array([160, 120,  70])
RED_UPPER2  = np.array([179, 255, 255])

GREEN_LOWER = np.array([36,  80,  40])
GREEN_UPPER = np.array([85, 255, 255])

MIN_AREA = 150


class PerceptionNode(Node):

    def __init__(self):
        super().__init__('perception_node')

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            rclpy.qos.qos_profile_sensor_data
        )

        self.detection_pub = self.create_publisher(Point, '/ball_detection', 10)

        self.get_logger().info('Perception node started — watching for red/green balls')

    # ── helpers ─────────────────────────────────────────────

    def find_best_circle(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        best = None
        best_area = MIN_AREA

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > best_area:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                if radius > 5:
                    best_area = area
                    best = (int(x), int(y), int(radius))
        return best

    # ── main callback ───────────────────────────────────────

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().warn(f'cv_bridge error: {e}')
            return

        # Blur + HSV
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv     = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # ── Masks ──
        mask_r1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
        mask_r2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
        mask_red = cv2.bitwise_or(mask_r1, mask_r2)

        mask_green = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)

        # Cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_red   = cv2.morphologyEx(mask_red,   cv2.MORPH_OPEN, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

        red_det   = self.find_best_circle(mask_red)
        green_det = self.find_best_circle(mask_green)

        detection = None
        color_name = ""

        if red_det and green_det:
            if red_det[2] >= green_det[2]:
                detection = red_det
                color_name = "RED"
            else:
                detection = green_det
                color_name = "GREEN"
        elif red_det:
            detection = red_det
            color_name = "RED"
        elif green_det:
            detection = green_det
            color_name = "GREEN"

        msg_out = Point()

        # ── DRAW DETECTION (🔥 NEW PART) ──
        if detection:
            cx, cy, radius = detection

            msg_out.x = float(cx)
            msg_out.y = float(cy)
            msg_out.z = float(radius)

            # Draw circle
            cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)

            # Draw center point
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

            # Label
            cv2.putText(frame, f"{color_name}",
                        (cx - 40, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        else:
            msg_out.x = 0.0
            msg_out.y = 0.0
            msg_out.z = 0.0

        self.detection_pub.publish(msg_out)

        # ── SHOW WINDOW (🔥 MOST IMPORTANT) ──
        cv2.imshow("Ball Detection", frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()   # 🔥 cleanup
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()#!/usr/bin/env python3
"""
perception_node.py
Shows detection using OpenCV window + publishes detection
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np


# ── HSV colour ranges ─────────────────────────────────────────────

RED_LOWER1  = np.array([0,   120,  70])
RED_UPPER1  = np.array([10,  255, 255])
RED_LOWER2  = np.array([160, 120,  70])
RED_UPPER2  = np.array([179, 255, 255])

GREEN_LOWER = np.array([36,  80,  40])
GREEN_UPPER = np.array([85, 255, 255])

MIN_AREA = 150


class PerceptionNode(Node):

    def __init__(self):
        super().__init__('perception_node')

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            rclpy.qos.qos_profile_sensor_data
        )

        self.detection_pub = self.create_publisher(Point, '/ball_detection', 10)

        self.get_logger().info('Perception node started — watching for red/green balls')

    # ── helpers ─────────────────────────────────────────────

    def find_best_circle(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        best = None
        best_area = MIN_AREA

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > best_area:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                if radius > 5:
                    best_area = area
                    best = (int(x), int(y), int(radius))
        return best

    # ── main callback ───────────────────────────────────────

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().warn(f'cv_bridge error: {e}')
            return

        # Blur + HSV
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv     = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # ── Masks ──
        mask_r1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
        mask_r2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
        mask_red = cv2.bitwise_or(mask_r1, mask_r2)

        mask_green = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)

        # Cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_red   = cv2.morphologyEx(mask_red,   cv2.MORPH_OPEN, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

        red_det   = self.find_best_circle(mask_red)
        green_det = self.find_best_circle(mask_green)

        detection = None
        color_name = ""

        if red_det and green_det:
            if red_det[2] >= green_det[2]:
                detection = red_det
                color_name = "RED"
            else:
                detection = green_det
                color_name = "GREEN"
        elif red_det:
            detection = red_det
            color_name = "RED"
        elif green_det:
            detection = green_det
            color_name = "GREEN"

        msg_out = Point()

        # ── DRAW DETECTION (🔥 NEW PART) ──
        if detection:
            cx, cy, radius = detection

            msg_out.x = float(cx)
            msg_out.y = float(cy)
            msg_out.z = float(radius)

            # Draw circle
            cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)

            # Draw center point
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

            # Label
            cv2.putText(frame, f"{color_name}",
                        (cx - 40, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        else:
            msg_out.x = 0.0
            msg_out.y = 0.0
            msg_out.z = 0.0

        self.detection_pub.publish(msg_out)

        # ── SHOW WINDOW (🔥 MOST IMPORTANT) ──
        cv2.imshow("Ball Detection", frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()   # 🔥 cleanup
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
