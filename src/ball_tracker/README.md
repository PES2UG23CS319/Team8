# Ball Tracker — ROS 2 Humble Autonomous Robot

Autonomous mobile robot that detects **red and green balls** using OpenCV HSV colour
detection and drives toward them using a simple perception → decision → control pipeline.

---

## Folder Structure
```

ball_tracker_ws/
└── src/
    └── ball_tracker/
        ├── ball_tracker/
        │   ├── __init__.py
        │   ├── perception_node.py     ← OpenCV HSV detector
        │   └── control_node.py        ← Velocity controller
        │
        ├── description/
        │   └── robot.urdf.xacro       ← Robot model + camera
        │
        ├── launch/
        │   ├── launch_sim.launch.py   ← Full system launcher
        │   └── rsp.launch.py          ← Robot state publisher
        │
        ├── worlds/
        │   └── ball_world.world       ← Gazebo world (red, green, blue balls)
        │
        ├── CMakeLists.txt
        ├── package.xml
        ├── setup.py
        ├── README.md
        └── .gitignore
```

---

## Prerequisites

Install required ROS 2 and system packages (run once):

```bash
sudo apt update

# Core ROS 2 tools
sudo apt install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    python3-opencv \
    python3-colcon-common-extensions
```

---

## Network Isolation (IMPORTANT — do this first)

If you are on a shared network, isolate your ROS traffic to avoid interference:

```bash
# Backup first
[ -e ~/bashrc.bak ] || cp ~/.bashrc ~/bashrc.bak

# Add isolation settings
echo '' >> ~/.bashrc
echo '# ROS 2 Network Isolation' >> ~/.bashrc
echo 'export ROS_DOMAIN_ID=42' >> ~/.bashrc
echo 'export ROS_LOCALHOST_ONLY=1' >> ~/.bashrc

# Apply immediately
source ~/.bashrc
```

---

## Build

```bash
# Navigate to workspace
cd ~/ball_tracker_ws

# Source ROS 2
source /opt/ros/humble/setup.bash

# Build the package
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

---

## Run

Open a terminal, source the workspace, and launch everything with one command:

```bash
source /opt/ros/humble/setup.bash
source ~/ball_tracker_ws/install/setup.bash

ros2 launch ball_tracker launch_sim.launch.py
```

This starts:
- **Gazebo** with the ball world (red, green, blue balls placed in front of the robot)
- **robot_state_publisher** (publishes URDF + TF)
- **spawn_entity** (spawns the robot at the origin)
- **perception_node** (starts after 5 s — detects red/green balls from camera)
- **control_node** (starts after 5 s — drives toward detected ball)

---

## What to Expect

1. Gazebo opens with a white box robot and three coloured balls ahead of it.
2. After ~5 seconds the perception and control nodes start.
3. The robot begins **rotating slowly** (SEARCH state) if no ball is visible.
4. Once a ball is in frame the robot **aligns** with it (ALIGN state), then **drives forward** (APPROACH state).
5. When the ball fills enough of the frame (radius ≥ 60 px), the terminal prints:

```
============================================
  *** TARGET REACHED! Ball is close enough. ***
  Stopping robot. Searching for next ball...
============================================
```

6. After 3 seconds the robot resumes searching for the remaining ball.

---

## ROS 2 Topics

| Topic               | Type                          | Direction          |
|---------------------|-------------------------------|--------------------|
| `/camera/image_raw` | `sensor_msgs/msg/Image`       | Gazebo → perception|
| `/ball_detection`   | `geometry_msgs/msg/Point`     | perception → control|
| `/cmd_vel`          | `geometry_msgs/msg/Twist`     | control → Gazebo   |
| `/robot_description`| `std_msgs/msg/String`         | RSP → Gazebo       |
| `/odom`             | `nav_msgs/msg/Odometry`       | Gazebo → (optional)|

Inspect topics with:
```bash
ros2 topic list
ros2 topic echo /ball_detection
ros2 topic echo /cmd_vel
```

---

## Tuning Parameters

Edit `ball_tracker/control_node.py` to adjust behaviour:

| Parameter         | Default | Effect                              |
|-------------------|---------|-------------------------------------|
| `CENTRE_TOLERANCE`| 30 px   | Dead-band for "centred" alignment   |
| `REACHED_RADIUS`  | 60 px   | Ball radius that triggers "reached" |
| `APPROACH_LINEAR` | 0.15 m/s| Forward speed when approaching      |
| `ALIGN_ANGULAR`   | 0.35 r/s| Rotation speed when aligning        |
| `SEARCH_ANGULAR`  | 0.40 r/s| Rotation speed while scanning       |

Edit `ball_tracker/perception_node.py` to adjust colour ranges:

```python
RED_LOWER1 / RED_UPPER1   # Red (hue 0–10)
RED_LOWER2 / RED_UPPER2   # Red (hue 160–179, wraps)
GREEN_LOWER / GREEN_UPPER # Green (hue 36–85)
```

---

## Troubleshooting

**Gazebo is very slow / crashes**
- Close other applications. With 4 GB RAM + 2 cores, Gazebo classic is borderline.
- Try setting `export LIBGL_ALWAYS_SOFTWARE=1` before launching if you have no GPU.

**Camera image not received**
```bash
ros2 topic list | grep camera
# Should show /camera/image_raw
ros2 topic hz /camera/image_raw
# Should show ~10 Hz
```

**Robot doesn't move**
```bash
ros2 topic echo /cmd_vel
# Should show non-zero values when ball is detected
ros2 topic echo /ball_detection
# z > 0 means a ball was found
```

**Build errors about cv_bridge**
```bash
sudo apt install ros-humble-cv-bridge python3-opencv
```

**"No executable found" error**
```bash
# Make sure scripts are executable
chmod +x ~/ball_tracker_ws/src/ball_tracker/ball_tracker/*.py
# Then rebuild
cd ~/ball_tracker_ws && colcon build --symlink-install
```

---

## Concepts Used (from Lab Exercises)

| Concept               | Where used                              |
|-----------------------|-----------------------------------------|
| URDF / Xacro          | `robot.urdf.xacro` — links, joints, materials |
| diff_drive plugin     | Gazebo motion control via `/cmd_vel`    |
| Camera plugin         | Gazebo camera → `/camera/image_raw`     |
| ROS 2 nodes           | `perception_node`, `control_node`       |
| ROS 2 topics          | `/ball_detection`, `/cmd_vel`           |
| cv_bridge             | ROS Image ↔ OpenCV Mat conversion       |
| HSV colour detection  | `cv2.inRange()` in perception node      |
| Launch files          | `launch_sim.launch.py` (rsp + Gazebo + nodes) |
| Collision / Inertia   | Added to all URDF links                 |
| Gazebo materials      | `<gazebo reference>` colour tags        |
| Caster wheel friction | `<mu1>/<mu2>` near-zero for caster      |
