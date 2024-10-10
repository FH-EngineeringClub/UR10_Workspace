"""
This file is to demo the movement range of the UR10 chess robot
"""

import math
import rtde_io
import rtde_receive
import rtde_control
import yaml

# Load configuration from config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Robot Configuration
HOSTNAME = config["robot"]["hostname"]  # The IP address of your Universal Robot
HOST_PORT = config["robot"]["host_port"]  # The port to send commands to the robot
RTDE_FREQUENCY = config["robot"]["rtde_frequency"]  # Hz to update data from robot

rtde_io_ = rtde_io.RTDEIOInterface(HOSTNAME, RTDE_FREQUENCY)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(HOSTNAME, RTDE_FREQUENCY)
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)

# home position (0, -90, 0, -90, 0, 0)


def position(base, shoulder, elbow, w1, w2, w3):
    control_interface.moveJ(  # Position 1
        [
            math.radians(base),
            math.radians(shoulder),
            math.radians(elbow),
            math.radians(w1),
            math.radians(w2),
            math.radians(w3),
        ],  # q: joint positions
        3.14,  # speed: joint speed of leading axis [rad/s]
        3.14,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


while True:
    position(-67, -87, -119, -63, 89, -101)  # home position
    position(-10, -92, -119, -55, 89, 0)
    position(37, -33, -148, -86, 86, 100)
    position(37, -88, -8, -170, 85, 100)
    position(-65, -88, -8, -170, 85, 100)
    position(-67, -87, -119, -63, 89, -101)  # home position

control_interface.stopScript()
