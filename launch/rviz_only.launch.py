import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'ros2_twsbr2'
    pkg_share = get_package_share_directory(pkg_name)
    
    # 1. Path to Xacro
    xacro_file = os.path.join(pkg_share, 'urdf', 'self_balancing_bot_fusion.xacro')

    # 2. Process Xacro
    # We use 'command' to process the xacro file into a pure URDF string
    doc = Command(['xacro ', xacro_file])

    # 3. Robot State Publisher
    # This publishes the 3D transforms (tf) for the robot
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': doc}]
    )

    # 4. Joint State Publisher GUI
    # This pops up a small window slider to move the wheels manually
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # 5. RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher_node,
        rviz_node
    ])
