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
sudo apt install build-essential cmake python3 python3-pip git python3.12-venv python3-colcon-common-extensions
```

### ROS 2 Jazzy
Follow the official ROS 2 Jazzy installation instructions.

Reference: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

```bash
mkdir -p ~/ros2_ws/src
```

After installing, source ROS 2:

```bash
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

### Gazebo Harmonic

```bash
sudo apt install ros-jazzy-ros-gz
```

Verify Gazebo:

```bash
gz sim
```

### PX4 X500 quadrotor

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
```

```bash
bash ./Tools/setup/ubuntu.sh --no-sim-tools
```
Restart the computer after installation, then verify PX4 builds.

```bash
cd ~/PX4-Autopilot
make px4_sitl
```

If Gazebo has rendering issues with OGRE2, force OGRE:

```bash
echo 'export PX4_GZ_SIM_RENDER_ENGINE=ogre' >> ~/.bashrc
source ~/.bashrc
```

Verify:
```bash
make px4_sitl gz_x500
```

### QGroundControl

You will need QGround Control to interface with PX4:

https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html

dependencies:
```bash
sudo apt install -y libfuse2 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor0
```

Make download executable and run it:
```bash
cd ~/Downloads
chmod +x QGroundControl-x86_64.AppImage
./QGroundControl-x86_64.AppImage
```

### GStreamer for Camera Support

```bash
sudo apt install \
gstreamer1.0-plugins-base \
gstreamer1.0-plugins-good \
gstreamer1.0-plugins-bad \
gstreamer1.0-plugins-ugly \
gstreamer1.0-libav \
libgstreamer-plugins-base1.0-dev
cd ~/PX4-Autopilot
rm -rf build/px4_sitl_default
make px4_sitl gz_x500_mono_cam
```
### Ultralytics

ROS->OpenCV bridge:
```bash
sudo apt install ros-jazzy-cv-bridge python3-opencv
```

Virtual environment for ultralytics
```bash
cd ~/ros2_ws
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

python -m pip install -U pip
python -m pip install "numpy==1.26.4" "setuptools<80" "opencv-python<4.12"
python -m pip install ultralytics
python -m pip check
```
### ROS to PX4 connector

```bash
cd ~/ros2_ws/src

git clone https://github.com/PX4/px4_msgs.git

git clone -b v2.4.3 \
https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
```

### Start DDS Agent

```bash
cd ~/ros2_ws
source install/setup.bash

MicroXRCEAgent udp4 -p 8888
```

### Slam

```bash
sudo apt update
sudo apt install ros-jazzy-slam-toolbox ros-jazzy-rviz2
```