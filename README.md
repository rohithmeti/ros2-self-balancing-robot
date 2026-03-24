# ROS 2 Two-Wheeled Self-Balancing Bot Simulation


### Project Description
A simulation package for a two-wheeled self-balancing robot utilizing ROS 2 Humble and Ignition Gazebo Fortress. The project simulates physics, collision, and sensor data (IMU) to develop and test balancing algorithms. It features a custom URDF model, a bidirectional bridge between ROS 2 and Gazebo, and a Python-based PID controller for active balancing.

---

### System Specifications & Prerequisites
* **OS:** Ubuntu 22.04 LTS (or Pop!_OS 22.04)
* **ROS Version:** ROS 2 Humble
* **Simulator:** Ignition Gazebo Fortress (Ignition 6)
* **MATLAB:** R2023b or newer recommended (Optional, for real-time data visualization and co-simulation)

---

### Comprehensive Installation & Setup
To ensure a smooth setup without "Package Not Found" errors, follow these steps sequentially. This covers all required bridges, URDF parsers, and state publishers.

**1. Install Core System Dependencies**
Open your terminal and run the following to install the essential ROS-Ignition bridges, Xacro (for parsing the robot model), and state publishers:
```bash
sudo apt update
sudo apt install -y \
  ros-humble-ros-ign-gazebo \
  ros-humble-ros-ign-bridge \
  ros-humble-ros-ign-interfaces \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  python3-colcon-common-extensions \
  python3-rosdep
