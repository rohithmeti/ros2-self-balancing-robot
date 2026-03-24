#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

# SETTINGS
MOVE_SPEED = 1.0
TURN_SPEED = 1.0

msg = """
---------------------------
   WASD BALANCING DRIVER
---------------------------
       W
   A   S   D

W: Lean Forward (Drive)
S: Lean Backward (Reverse)
A: Spin Left
D: Spin Right


CTRL-C: Quit
---------------------------
"""

class WASDDriver(Node):
    def __init__(self):
        super().__init__('wasd_driver')
        # Publish to the specific topic our Balance Controller listens to
        self.pub = self.create_publisher(Twist, '/teleop_cmd', 10)
        self.timer = self.create_timer(0.1, self.publish_command)
        self.settings = termios.tcgetattr(sys.stdin)
        self.key = None
        print(msg)

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish_command(self):
        key = self.getKey()
        twist = Twist()

        # LOGIC: Hold Key -> Move. Release -> Stop.
        if key == 'w':
            twist.linear.x = MOVE_SPEED
        elif key == 's':
            twist.linear.x = -MOVE_SPEED
        elif key == 'a':
            twist.angular.z = -TURN_SPEED
        elif key == 'd':
            twist.angular.z = TURN_SPEED
        elif key == ' ':
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif key == '\x03': # CTRL-C
            self.destroy_node()
            rclpy.shutdown()
            exit()
        else:
            # If no key is pressed, send ZEROS (Balance in place)
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.pub.publish(twist)

def main():
    rclpy.init()
    node = WASDDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
