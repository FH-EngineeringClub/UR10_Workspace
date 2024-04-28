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


position(-67, -87, -119, -63, 89, -101)  # home position
position(-18, -77, -97, -96, 86, -52)  # lift up
position(15, -60, -149, -62, 86, -18)  # lift down
position(61, -158, -18, -97, 88, 41)  # behind robot
position(15, -60, -149, -62, 86, -18)  # lift down
position(-18, -77, -97, -96, 86, -52)  # lift up
position(-67, -87, -119, -63, 89, -101)  # home position
