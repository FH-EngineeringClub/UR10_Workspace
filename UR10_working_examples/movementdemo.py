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


def position_3():
    control_interface.moveJ(  # Position 2
        [
            math.radians(-273),
            math.radians(-142),
            math.radians(-43),
            math.radians(255),
            math.radians(66),
            math.radians(-86),
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


def position_4():
    control_interface.moveJ(  # Position 2
        [
            math.radians(-303),
            math.radians(-176),
            math.radians(16),
            math.radians(281),
            math.radians(95),
            math.radians(-86),
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


def position_5():
    control_interface.moveJ(  # Position 2
        [
            math.radians(-302),
            math.radians(-164),
            math.radians(108),
            math.radians(220),
            math.radians(144),
            math.radians(-86),
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


def position_6():
    control_interface.moveJ(  # Position 2
        [
            math.radians(-328),
            math.radians(-96),
            math.radians(64),
            math.radians(216),
            math.radians(224),
            math.radians(-86),
        ],  # q: joint positions
        0.5,  # speed: joint speed of leading axis [rad/s]
        0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
    )


for _ in range(5):
    position_0()
    position_1()
    position_2()
    position_3()
    position_4()
    position_5()
    position_6()

# position_1()
# position_0()
