# Software Requirements Specification

## Requirements

### FR-001
System shall provide a limited 3D space for simulations.

### FR-002
System shall provide a human target object.

### FR-003
System shall provide a single UAV.

### FR-004
System shall place the drone at known starting location when the mission begins.

### FR-005
System shall provide obstacles in the simulation space.

### FR-006
The UAV shall navigate through the environment without manual control.

### FR-007
The UAV shall search for the target object without manual control.

### FR-008
The UAV shall recognize the target object using a simulated camera.

### FR-009
The UAV shall record the target object's approximate location.

### FR-010
The UAV shall report mission successful if target object is located.

### FR-011
System shall display target objects approximate location.

### FR-012
System shall provide non-target objects.

### FR-013
The UAV shall distinguish target objects from non-target objects.

### FR-016
The UAV shall report mission failure if target object is not located.

## Definitions
ROS - Robot Operating System is a framework for robotics that helps parts of a robot communicate.  
ROS node - represents one running program/components.  
ROS topic - A named stream of data.  
ROS message - Structure of data being transmitted.   
ROS publisher - A node that sends data onto a topic.  
ROS subscriber - A node that listens to a topic.  
ros_gz - Integration packages that connect ROS 2 with Gazebo.  
colcon - Build tool commonly used to build ROS 2 workspaces.  
rosdep - Tool that identifies and installs dependencies required by ROS packages.  