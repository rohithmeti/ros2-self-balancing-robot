#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import math

# =========================================
# TUNING (STABILITY FOCUSED)
# =========================================
KP = 18.0   
KD = 2.5    
KI = 0.0 

# SETTINGS
MAX_TILT = 30.0     

# TURNING FIXES
TURN_SPEED = 0.5        # Lowered from 0.8 to stop spinning
TURN_SLEW_STEP = 0.02   # Ramps turning VERY slowly to prevent violent snaps

# DRIVING FIXES
DRIVE_TILT_ANGLE = 3.0  
DRIVE_SLEW_STEP = 0.05  # Smooth acceleration
STABLE_LIMIT = 3.0      

# MECHANICAL ZERO
TARGET_ANGLE = 0.0    

class SwitchingController(Node):
    def __init__(self):
        super().__init__('switching_controller')
        self.sub_imu = self.create_subscription(Imu, '/imu', self.imu_callback, 10)
        self.sub_teleop = self.create_subscription(Twist, '/teleop_cmd', self.teleop_callback, 10)
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.prev_error = 0.0
        
        # User Inputs
        self.user_turn_input = 0.0 
        self.desired_lean = 0.0   
        
        # Ramped (Smoothed) Values
        self.current_lean = 0.0   
        self.current_turn = 0.0   
        
        self.get_logger().info("Final Stable wasd user wasd terminal Controller Active.")

    def teleop_callback(self, msg):
        # 1. Map 'W'/'S' to LEAN ANGLE
        if msg.linear.x > 0:
            self.desired_lean = -DRIVE_TILT_ANGLE 
        elif msg.linear.x < 0:
            self.desired_lean = DRIVE_TILT_ANGLE  
        else:
            self.desired_lean = 0.0
            
        # 2. Store Turn Command
        self.user_turn_input = msg.angular.z

    def imu_callback(self, msg):
        # --- A. RAMPING (The Fix for Violence) ---
        
        # 1. Ramp the Lean (Forward/Back)
        lean_diff = self.desired_lean - self.current_lean
        if abs(lean_diff) < DRIVE_SLEW_STEP:
            self.current_lean = self.desired_lean
        else:
            self.current_lean += math.copysign(DRIVE_SLEW_STEP, lean_diff)

        # 2. Ramp the Turn (Left/Right) - CRITICAL FIX
        target_turn = self.user_turn_input * TURN_SPEED
        turn_diff = target_turn - self.current_turn
        
        if abs(turn_diff) < TURN_SLEW_STEP:
            self.current_turn = target_turn
        else:
            self.current_turn += math.copysign(TURN_SLEW_STEP, turn_diff)

        # --- B. SENSOR CALCULATION ---
        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w
        sinr = 2 * (qw * qx + qy * qz)
        cosr = 1 - 2 * (qx * qx + qy * qy)
        current_angle = math.degrees(math.atan2(sinr, cosr))
        
        if abs(current_angle) > MAX_TILT:
            self.stop_robot()
            return

        # --- C. SWITCHING LOGIC ---
        
        # The angle we WANT to be at right now (e.g. -3.0 deg)
        active_target = TARGET_ANGLE + self.current_lean
        
        # How far are we from that angle?
        deviation = current_angle - active_target

        # MODE A: RESCUE (Unstable)
        if abs(deviation) > STABLE_LIMIT:
            # Full Balance Power
            error = active_target - current_angle
            p_out = KP * error
            d_out = KD * (error - self.prev_error)
            output = -(p_out + d_out)
            self.prev_error = error
            
            # EMERGENCY: Cut turning to 0.0 to save the robot
            self.publish_cmd(output, 0.0)
            
        # MODE B: MANEUVER (Stable)
        else:
            # We are stable. Allow turning.
            error = active_target - current_angle
            
            p_out = KP * error
            d_out = KD * (error - self.prev_error)
            
            # Reduce Jitter: Use 60% power for holding angle, not 80%
            balance_force = -(p_out + d_out) * 0.6
            
            # Use the RAMPED turn value (not raw input)
            self.prev_error = error
            self.publish_cmd(balance_force, self.current_turn)

    def publish_cmd(self, linear_speed, angular_speed):
        t = Twist()
        # Clamp max speed strictly
        t.linear.x = float(max(min(linear_speed, 5.0), -5.0))
        t.angular.z = float(angular_speed)
        self.pub_vel.publish(t)

    def stop_robot(self):
        self.pub_vel.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = SwitchingController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
