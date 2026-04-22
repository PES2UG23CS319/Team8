"""
launch_sim.launch.py
====================
Starts:
  1. robot_state_publisher  (with xacro URDF)
  2. Gazebo                 (with custom ball world)
  3. spawn_entity           (spawns robot into Gazebo)
  4. perception_node        (OpenCV HSV ball detector)
  5. control_node           (velocity controller)
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory('ball_tracker')
    world_file = os.path.join(pkg, 'worlds', 'ball_world.world')

    # ── 1. robot_state_publisher ──────────────────────────────────────────
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # ── 2. Gazebo (classic) ───────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch', 'gazebo.launch.py'
            )
        ),
        launch_arguments={
            'world': world_file,
            # Keep performance reasonable on low-spec VM
            'verbose': 'false',
            'pause':   'false',
        }.items()
    )

    # ── 3. Spawn robot ────────────────────────────────────────────────────
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'ball_tracker_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
        ],
        output='screen'
    )

    # ── 4. Perception node ────────────────────────────────────────────────
    perception_node = Node(
        package='ball_tracker',
        executable='perception_node.py',
        name='perception_node',
        output='screen'
    )

    # ── 5. Control node ───────────────────────────────────────────────────
    control_node = Node(
        package='ball_tracker',
        executable='control_node.py',
        name='control_node',
        output='screen'
    )

    # Delay perception & control slightly to let Gazebo + camera come up
    delayed_nodes = TimerAction(
        period=5.0,
        actions=[perception_node, control_node]
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        delayed_nodes,
    ])
