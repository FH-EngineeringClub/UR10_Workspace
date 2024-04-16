"""
This file is to demo the movement range of the UR10 chess robot
"""

import math
import rtde_io
import rtde_receive
import rtde_control

HOSTNAME = "192.168.2.81"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot
RTDE_FREQUENCY = 10  # Hz to update data from robot

rtde_io_ = rtde_io.RTDEIOInterface(HOSTNAME, RTDE_FREQUENCY)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(HOSTNAME, RTDE_FREQUENCY)
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)

# home position (0, -90, 0, -90, 0, 0)
base_radians = math.radians(-278)
shoulder_radians = math.radians(-92)
elbow_radians = math.radians(120)
wrist_1_radians = math.radians(242)
wrist_2_radians = math.radians(268)
wrist_3_radians = math.radians(-125)


def position_0():
    control_interface.moveJ(  # Home position
        [
            base_radians,
            shoulder_radians,
            elbow_radians,
            wrist_1_radians,
            wrist_2_radians,
            wrist_3_radians,
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


def position_1():
    control_interface.moveJ(  # Position 1
        [
            math.radians(-288),
            math.radians(-89),
            math.radians(-1),
            math.radians(270),
            math.radians(180),
            math.radians(-127),
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


def position_2():
    control_interface.moveJ(  # Position 2
        [
            math.radians(-196),
            math.radians(-89),
            math.radians(-1),
            math.radians(155),
            math.radians(33),
            math.radians(-86),
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


position_0()
position_1()
position_2()
position_1()
position_0()
