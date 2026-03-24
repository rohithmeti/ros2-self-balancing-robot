#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import math

# --- TUNING CONSTANTS (We will tweak these) ---
# Start with P only. Keep I and D low.
KP = 9.0   # Reaction strength (Senior's code used a calculated value, we start clean)
KI = 0.0   # Integral (Fixes drift, but adds instability)
KD = 1.5   # Derivative (Dampening/Shock Absorber)

# --- SETTINGS ---
TARGET_ANGLE = 0.0# Mechanical Zero (Degrees). Change this if it drifts.
MAX_TILT = 30.0     # Kill motors if angle > 30 degrees (Safety)

class SelfBalanceController(Node):
    def __init__(self):
        super().__init__('self_balance_controller')
        
        # Subscribe to IMU
        self.subscription = self.create_subscription(
            Imu, 
            '/imu', 
            self.imu_callback, 
            10)
            
        # Publish to Wheels (DiffDrive Plugin)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # PID Memory Variables
        self.prev_error = 0.0
        self.integral = 0.0
        
        self.get_logger().info("PID Controller Started. Balancing at " + str(TARGET_ANGLE) + " degrees.")

    def imu_callback(self, msg):
        # 1. GET TILT ANGLE (ROLL)
        # Your IMU is sideways, so we use X/Y/Z/W to calculate Roll.
        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w
        
        # Standard conversion from Quaternion to Roll (Radians)
        sinr_cosp = 2 * (qw * qx + qy * qz)
        cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
        current_angle_rad = math.atan2(sinr_cosp, cosr_cosp)
        
        # Convert to Degrees
        current_angle = math.degrees(current_angle_rad)
        
        # 2. SAFETY CHECK (The "Kill Switch")
        # If the robot is lying on the floor, STOP. Don't spin wheels.
        if abs(current_angle) > MAX_TILT:
            self.stop_robot()
            return

        # 3. PID CALCULATION
        # Error = Where we want to be - Where we are
        error = TARGET_ANGLE - current_angle
        
        # P Term (Proportional)
        p_out = KP * error
        
        # I Term (Integral)
        self.integral += error
        # Anti-windup (Like your seniors did): Clamp the integral
        self.integral = max(min(self.integral, 100.0), -100.0) 
        i_out = KI * self.integral
        
        # D Term (Derivative)
        derivative = error - self.prev_error
        d_out = KD * derivative
        
        # Combine
        output = -(p_out + i_out + d_out)
        
        self.prev_error = error
        
        # 4. SEND COMMAND
        # NOTE: We might need to flip the sign (-output) depending on motor wiring.
        # If it drives INTO the fall (good), keep it. 
        # If it drives AWAY from the fall (bad), flip sign to: -output
        self.publish_cmd(output)

    def publish_cmd(self, speed):
        # Limit max speed to 2.0 m/s
        speed = max(min(speed, 2.0), -2.0)
        
        twist = Twist()
        twist.linear.x = float(speed)
        twist.angular.z = 0.0
        self.publisher_.publish(twist)

    def stop_robot(self):
        self.publisher_.publish(Twist()) # Send zeros

def main(args=None):
    rclpy.init(args=args)
    node = SelfBalanceController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
