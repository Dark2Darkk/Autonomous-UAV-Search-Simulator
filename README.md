## Prerequisites

This project is developed and tested on:
- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Gazebo Harmonic
- Python3
- Git
- CMake

## Installation

### Developer Tools

```bash
sudo apt update
sudo apt install build-essential cmake python3 python3-pip python3-venv git
```

### ROS 2 Jazzy 
Follow the official ROS 2 Jazzy installation instructions.

Reference: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

After installing, source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

### Gazebo Harmonic

```bash
sudo apt install ros-jazzy-ros-gz
```

Source ROS 2 if necessary:

```bash
source /opt/ros/jazzy/setup.bash
```

Verify Gazebo:

```bash
gz sim
```

