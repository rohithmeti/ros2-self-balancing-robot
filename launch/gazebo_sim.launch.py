import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'ros2_twsbr2'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. SETUP GAZEBO RESOURCE PATH (The Fix)
    # This tells Gazebo where to look for "package://ros2_twsbr2/meshes..."
    # We add the parent directory of 'share' to the search path.
    install_dir = os.path.dirname(pkg_share) # returns .../install/ros2_twsbr2/share
    pkg_prefix = os.path.dirname(install_dir) # returns .../install/ros2_twsbr2
    
    # We append the 'share' directory to the resource path
    gazebo_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[os.path.join(pkg_prefix, 'share')]
    )

    # 2. Process Xacro
    xacro_file = os.path.join(pkg_share, 'urdf', 'self_balancing_bot_fusion.xacro')
    doc = Command(['xacro ', xacro_file])

    # 3. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': doc, 'use_sim_time': True}]
    )

# 4. Ignition Gazebo (Uneven World)
    # Get path to our new world file
    world_file = os.path.join(pkg_share, 'worlds', 'ramps.sdf')

    ign_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_ign_gazebo'),
                         'launch', 'ign_gazebo.launch.py')
        ),
        # TELL IGNITION TO OPEN OUR RAMP WORLD
        launch_arguments={'ign_args': f'-r {world_file}'}.items()
    )
       





    # 5. Spawn Entity
    spawn_entity = Node(
        package='ros_ign_gazebo',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'self_balancing_bot',
                   '-z', '0.2'], # Spawn slightly in the air
        output='screen'
    )

# 6. Bridge (IMU + Clock + Cmd_Vel + ODOMETRY)
    bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            
            # IMU
            '/imu@sensor_msgs/msg/Imu@ignition.msgs.IMU',
            
            # Velocity Command
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',

            # --- NEW: ODOMETRY BRIDGE ---
            '/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
            
            # --- NEW: TF BRIDGE (For RViz Position) ---
            '/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_resource_path,
        ign_gazebo,
        robot_state_publisher,    
        spawn_entity,
        bridge
    ])
