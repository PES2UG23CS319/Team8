# 🤖 Detection of Red and Green Balls using Computer Vision (ROS2 + Gazebo)

## 📌 Overview

This project implements a perception-based robotic system using **ROS2**, **Gazebo**, and **OpenCV**.
A robot equipped with a camera detects **red and green balls** in a simulated environment in real time.

---

## 🎯 Features

* Real-time camera-based object detection
* Color-based detection using OpenCV (HSV)
* Simulation using Gazebo
* Modular ROS2 architecture (nodes + topics)

---

## 🧠 System Architecture

```
Gazebo → Robot → Camera → /camera/image_raw → Perception Node → OpenCV → Detection Output
```

---

## 🛠️ Technologies Used

* ROS2 (Humble)
* Python
* OpenCV
* Gazebo
* URDF (Robot modeling)

---

## 📂 Project Structure

```
ball_tracker_ws/
│── src/
│   └── ball_tracker/
│       ├── launch/
│       │   └── launch_sim.launch.py
│       ├── urdf/
│       │   └── robot.urdf
│       ├── worlds/
│       │   └── ball_world.world
│       ├── ball_tracker/
│       │   ├── perception_node.py
│       │   └── control_node.py (optional)
│       ├── package.xml
│       └── setup.py
```

---

## 🚀 How to Run

### 1️⃣ Build the workspace

```bash
cd ~/Downloads/ball_tracker_ws
colcon build --symlink-install
```

### 2️⃣ Source environment

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

### 3️⃣ Kill previous Gazebo processes (important)

```bash
killall -9 gzserver gzclient gazebo
```

### 4️⃣ Fix VM graphics (if using VM)

```bash
export DISPLAY=:0
export LIBGL_ALWAYS_SOFTWARE=1
```

### 5️⃣ Run the project

```bash
ros2 launch ball_tracker launch_sim.launch.py
```

---

## 🎮 Optional: Teleop Control

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Controls:

```
i → forward  
k → stop  
j → left  
l → right  
```

---

## 🧠 How It Works

1. The robot camera captures images in Gazebo
2. Images are published to `/camera/image_raw`
3. The perception node subscribes to this topic
4. OpenCV processes the image:

   * Converts to HSV
   * Applies color masks (red & green)
   * Detects contours
5. Detected objects are highlighted in real time

---

## 📸 Results

* Gazebo simulation with robot and colored balls
* OpenCV window showing detected red and green balls
* Real-time processing achieved

---

## 👥 Team Contributions

Maitreyi — System Integration & Launch (launch_sim.launch.py)
- Initialize Gazebo simulation
- Load custom world environment
- Spawn robot model into simulation
- Launch perception node and manage system startup

Atharv — Simulation Environment (ball_world.world)
- Design ground plane and lighting
- Create and configure ball models (red, green, blue)
- Define object positions in the environment

Mansha — Robot Modeling (robot.urdf.xacro)
- Define robot base and chassis structure
- Configure wheels and joints
- Attach and position camera link
- Integrate camera sensor plugin

Manaswi — Perception System (perception_node.py)
- Subscribe to camera image topic
- Convert ROS image to OpenCV format
- Perform HSV color space conversion
- Detect contours and visualize output

## 📎 Demo

https://drive.google.com/file/d/1s58ECUUtk7f50d6HpEJxGDv-Gjr3ZZUG/view?usp=drive_link
---


## 🏁 Conclusion

This project demonstrates how perception, simulation, and ROS2 communication can be integrated to build intelligent robotic systems.

---
