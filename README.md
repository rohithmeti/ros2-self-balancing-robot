

```markdown
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
```

**2. Create the Workspace & Clone**
Navigate to your workspace root directory and clone the repository:
```bash
mkdir -p ~/ros2_twsbr2_ws/src
cd ~/ros2_twsbr2_ws/src
git clone https://github.com/rohithmeti/ros2-self-balancing-robot.git
```

**3. Run Rosdep (The Safety Net)**
`rosdep` will scan the `package.xml` file and automatically install any other underlying dependencies required by this specific package:
```bash
cd ~/ros2_twsbr2_ws
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

**4. Build the Workspace**
Build the package using colcon. The `--symlink-install` flag is highly recommended for Python development so you don't have to rebuild every time you edit a script:
```bash
colcon build --symlink-install
```

**5. Source the Environment**
Before running any commands, you must source the setup file in every new terminal window:
```bash
source install/setup.bash
```
*(Tip: Add `source ~/ros2_twsbr2_ws/install/setup.bash` to your `~/.bashrc` to do this automatically).*

---

### Execution Instructions

**Step 1: Launch the Simulation**
This command opens Ignition Gazebo, parses the Xacro file, spawns the robot model, and starts the ROS-Ignition bridge:
```bash
ros2 launch ros2_twsbr2 gazebo_sim.launch.py
```
<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/9ff8e5f8-e73d-473c-9d27-5fb4cc69ca54" />

*Note: Ensure you press the "Play" button in Gazebo if the physics are paused. The robot will fall over initially until a controller node is started.*

**Step 2: Run a Controller Node**
You have two options depending on what you want to test. Open a **new terminal**, source your workspace (`source install/setup.bash`), and choose one:

**Option A: Strict Balancing Only (No Movement)**
Use this to simply verify the PID logic holding the robot at $0^\circ$ against gravity and disturbances.
```bash
ros2 run ros2_twsbr2 only_self_balance_pid.py
```

**Option B: Balancing + Teleoperation (Drive the Robot)**
Use this to manually drive the robot. This requires running two separate nodes.
In Terminal 1 (The Brain):
```bash
ros2 run ros2_twsbr2 self_balance_controller.py
```
In Terminal 2 (The Keyboard Driver):
```bash
ros2 run ros2_twsbr2 wasd_driver.py
```
* **W:** Lean Forward (Drive)
* **S:** Lean Backward (Reverse)
* **A:** Spin Left (Zero-radius turn)
* **D:** Spin Right (Zero-radius turn)
* **Spacebar:** Stop moving and hold balance

**Step 3: (Optional) Run Motor Check**
To verify that the motors are spinning in the correct direction (forward/backward) without the PID logic active:
```bash
ros2 run ros2_twsbr2 check_motors.py
```

---

### MATLAB Integration
* **Status:** Successfully connected MATLAB to the ROS 2 network.
* **Functionality:** A MATLAB node is configured to subscribe to the `/imu` topic via the bridge.
* **Visualization:** Includes a script to convert Quaternion data to Euler angles (Pitch) and graph the robot's tilt in real-time to assist with PID tuning.

---

### Troubleshooting & Common Fixes

* **"Package 'ros_ign_gazebo' not found":** You missed Step 1. Run `sudo apt install ros-humble-ros-ign-gazebo ros-humble-ros-ign-bridge`.
* **"No executable found" for Python scripts:** Ensure you have built the workspace, sourced the setup file, and that the Python scripts in your `src` folder have executable permissions. If not, run:
  ```bash
  chmod +x ~/ros2_twsbr2_ws/src/ros2_twsbr2/ros2_twsbr2/*.py
  colcon build --symlink-install
  ```
* **"Package 'ros2_twsbr2' not found" during launch:** Your terminal doesn't know where your workspace is. Source it, or manually export the path:
  ```bash
  export AMENT_PREFIX_PATH=$AMENT_PREFIX_PATH:~/ros2_twsbr2_ws/install/ros2_twsbr2
 
