#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math

# =========================================
# 1. BALANCING TUNING (Inner Loop)
# =========================================
BAL_KP = 18.0   # Reaction to Angle
BAL_KD = 1.5    # Damping for Angle
BAL_KI = 0.0

# =========================================
# 2. POSITION TUNING (Outer Loop)
# =========================================
# How much to lean to fix drift?
# If drifting 1 meter, lean 3.0 degrees.
POS_KP = 3.0    
# Damping for Position (Uses Velocity). 
# Prevents overshooting the home position.
POS_KD = 0.8    

# Safety
MAX_TILT = 30.0

class PositionHold(Node):
    def __init__(self):
        super().__init__('position_hold_controller')
        
        # Subscribe to IMU (Fast - 100Hz+)
        self.sub_imu = self.create_subscription(
            Imu, '/imu', self.imu_callback, 10)
            
        # Subscribe to Odom (Position - Usually 20-50Hz)
        self.sub_odom = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
            
        # Publish Command
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # State Variables
        self.current_pos = 0.0
        self.current_vel = 0.0
        self.target_pos = 0.0  # We want to stay at X=0
        
        # PID Memory
        self.prev_bal_error = 0.0
        self.bal_integral = 0.0
        
        self.get_logger().info("Position Hold Controller Started!")
        self.get_logger().info("I will lean to resist drift.")

    def odom_callback(self, msg):
        # Update Position and Velocity from Virtual Encoders
        self.current_pos = msg.pose.pose.position.x
        self.current_vel = msg.twist.twist.linear.x

    def imu_callback(self, msg):
        # --- 1. CALCULATE TILT (Roll) ---
        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w
        sinr = 2 * (qw * qx + qy * qz)
        cosr = 1 - 2 * (qx * qx + qy * qy)
        angle = math.degrees(math.atan2(sinr, cosr))
        
        # Safety Kill
        if abs(angle) > MAX_TILT:
            self.stop_robot()
            return

        # --- 2. OUTER LOOP (Position Control) ---
        # Goal: Keep Position at 0.
        # Logic: If Position is + (Forward), we need to drive Backward.
        # To drive Backward, we need to lean Backward (+ Angle).
        # So Target Angle should be proportional to Position Error.
        
        pos_error = self.current_pos - self.target_pos
        
        # Calculate Desired Lean Angle based on Position
        # POS_KD * current_vel acts as a brake
        target_angle = (pos_error * POS_KP) + (self.current_vel * POS_KD)
        
        # Clamp the target angle so it doesn't try to lean 90 degrees to fix 1 meter
        target_angle = max(min(target_angle, 10.0), -10.0)

        # --- 3. INNER LOOP (Balance Control) ---
        # Now we balance at that calculated target angle
        bal_error = target_angle - angle
        
        p_out = BAL_KP * bal_error
        d_out = BAL_KD * (bal_error - self.prev_bal_error)
        
        # Integrate
        self.bal_integral += bal_error
        self.bal_integral = max(min(self.bal_integral, 50.0), -50.0)
        i_out = BAL_KI * self.bal_integral
        
        # Final Output (Motor Speed)
        # Sign check: Falling Forward (+) -> Needs Forward Speed (+)
        # Error is (Target - Current). If falling forward, Error is negative.
        # We need positive output. So invert.
        output = -(p_out + d_out + i_out)
        
        self.prev_bal_error = bal_error
        
        self.publish_cmd(output)

    def publish_cmd(self, linear_speed):
        linear_speed = max(min(linear_speed, 5.0), -5.0)
        t = Twist()
        t.linear.x = float(linear_speed)
        self.pub_vel.publish(t)

    def stop_robot(self):
        self.pub_vel.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = PositionHold()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
