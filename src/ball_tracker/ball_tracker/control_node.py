#!/usr/bin/env python3
"""
control_node.py
===============
Subscribes to /ball_detection (geometry_msgs/Point) and publishes
velocity commands to /cmd_vel (geometry_msgs/Twist).

State machine
─────────────
  SEARCH   – no ball visible → rotate slowly to scan
  ALIGN    – ball visible, off-centre → rotate to centre the ball
  APPROACH – ball centred → drive forward
  REACHED  – ball radius exceeds threshold → stop, announce, move to next colour

The node prints a clear "Target reached!" message when close enough.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point

# ── Tuning parameters ──────────────────────────────────────────────────────
IMAGE_WIDTH      = 320          # must match camera resolution
IMAGE_HEIGHT     = 240

CENTRE_TOLERANCE = 30           # pixels: ± band considered "centred"
REACHED_RADIUS   = 60           # pixels: ball radius that means "close enough"

SEARCH_ANGULAR   = 0.4          # rad/s while scanning
ALIGN_ANGULAR    = 0.35         # rad/s while aligning
APPROACH_LINEAR  = 0.15         # m/s while driving forward

# Slow down when almost aligned (dead-band tightening)
SLOW_ALIGN_THRESH = 60          # pixels from centre → use slower turn
SLOW_ALIGN_ANGULAR = 0.18

CONTROL_HZ       = 10.0         # publishing rate


class State:
    SEARCH   = 'SEARCH'
    ALIGN    = 'ALIGN'
    APPROACH = 'APPROACH'
    REACHED  = 'REACHED'


class ControlNode(Node):

    def __init__(self):
        super().__init__('control_node')

        self.detection_sub = self.create_subscription(
            Point, '/ball_detection', self.detection_callback, 10)

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer drives the control loop at a fixed rate
        self.timer = self.create_timer(1.0 / CONTROL_HZ, self.control_loop)

        # Latest detection (updated by subscriber)
        self.ball_x      = 0.0
        self.ball_y      = 0.0
        self.ball_radius = 0.0
        self.ball_found  = False

        self.state = State.SEARCH
        self.image_cx = IMAGE_WIDTH / 2.0      # image horizontal centre

        self.get_logger().info('Control node started')

    # ── subscriber ────────────────────────────────────────────────────────

    def detection_callback(self, msg: Point):
        self.ball_radius = msg.z
        if msg.z > 0:
            self.ball_x     = msg.x
            self.ball_y     = msg.y
            self.ball_found = True
        else:
            self.ball_found = False

    # ── control loop ──────────────────────────────────────────────────────

    def control_loop(self):
        twist = Twist()     # default: all zeros (stop)

        if self.state == State.REACHED:
            # Stay stopped; next ball search handled below
            self.cmd_vel_pub.publish(twist)
            return

        # ── Transition logic ───────────────────────────────────────────
        if not self.ball_found:
            self.state = State.SEARCH

        elif self.ball_radius >= REACHED_RADIUS:
            if self.state != State.REACHED:
                self.state = State.REACHED
                self.get_logger().info(
                    '============================================')
                self.get_logger().info(
                    '  *** TARGET REACHED! Ball is close enough. ***')
                self.get_logger().info(
                    '  Stopping robot. Searching for next ball...')
                self.get_logger().info(
                    '============================================')
                # Stop immediately, then re-enter SEARCH after a brief pause
                self.cmd_vel_pub.publish(twist)
                # Reset after 3 seconds to look for the next ball
                self.create_timer(3.0, self._reset_to_search)
            return

        else:
            error = self.ball_x - self.image_cx
            if abs(error) <= CENTRE_TOLERANCE:
                self.state = State.APPROACH
            else:
                self.state = State.ALIGN

        # ── Velocity commands ──────────────────────────────────────────
        if self.state == State.SEARCH:
            twist.angular.z = SEARCH_ANGULAR
            self.get_logger().debug('SEARCH: rotating to find ball')

        elif self.state == State.ALIGN:
            error = self.ball_x - self.image_cx
            # Negative error → ball is to the left → turn left (positive z)
            # Positive error → ball is to the right → turn right (negative z)
            if abs(error) > SLOW_ALIGN_THRESH:
                speed = ALIGN_ANGULAR
            else:
                speed = SLOW_ALIGN_ANGULAR

            twist.angular.z = -speed if error > 0 else speed
            self.get_logger().debug(
                f'ALIGN: error={error:.0f}px  angular={twist.angular.z:.2f}')

        elif self.state == State.APPROACH:
            twist.linear.x  = APPROACH_LINEAR
            twist.angular.z = 0.0
            self.get_logger().debug(
                f'APPROACH: radius={self.ball_radius:.0f}px')

        self.cmd_vel_pub.publish(twist)

    def _reset_to_search(self):
        """Called once (via one-shot timer) after reaching a target."""
        self.state = State.SEARCH
        self.get_logger().info('Resuming SEARCH for next ball...')


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Send a stop command on shutdown
        stop = Twist()
        node.cmd_vel_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
