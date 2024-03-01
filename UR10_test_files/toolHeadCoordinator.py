import math
from time import sleep
import rtde_io
import rtde_receive
import rtde_control

rtde_io_ = rtde_io.RTDEIOInterface("192.168.56.101")
rtde_receive_ = rtde_receive.RTDEReceiveInterface("192.168.56.101")
control_interface = rtde_control.RTDEControlInterface("192.168.56.101")

# Set the tool digital output on and off
print("tool on")
rtde_io_.setToolDigitalOut(0, True)
sleep(3)
rtde_io_.setToolDigitalOut(0, False)
print("tool off")


# home position (0, -90, 0, -90, 0, 0)
base_radians = math.radians(0)
shoulder_radians = math.radians(-90)
elbow_radians = math.radians(0)
wrist_1_radians = math.radians(-90)
wrist_2_radians = math.radians(0)
wrist_3_radians = math.radians(0)

# control_interface.getCurrentPosition()
control_interface.moveJ(
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
