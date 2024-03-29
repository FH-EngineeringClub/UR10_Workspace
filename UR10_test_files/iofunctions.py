import math
import json
import rtde_io
import rtde_receive
import rtde_control

rtde_io_ = rtde_io.RTDEIOInterface("192.168.2.81")
rtde_receive_ = rtde_receive.RTDEReceiveInterface("192.168.2.81")
control_interface = rtde_control.RTDEControlInterface("192.168.2.81")

# Set the tool digital output on and off
rtde_io_.setToolDigitalOut(0, True)
print("tool on")
# sleep(3)
rtde_io_.setToolDigitalOut(0, False)
print("tool off")

# Opening JSON file
f = open("positions.json", encoding="utf-8")
data = json.load(f)

input_position = input("Enter the position: ")

position = data[input_position]
radians = [math.radians(i) for i in position]

print(radians)
print(rtde_control.getForwardKinematics(radians))

# home position (0, -90, 0, -90, 0, 0)
base_radians = math.radians(0)
shoulder_radians = math.radians(-90)
elbow_radians = math.radians(0)
wrist_1_radians = math.radians(-90)
wrist_2_radians = math.radians(0)
wrist_3_radians = math.radians(0)

# control_interface.getCurrentPosition()
control_interface.moveJ(
    radians,  # q: joint positions
    0.5,  # speed: joint speed of leading axis [rad/s]
    0.5,  # acceleration: joint acceleration of leading axis [rad/s^2]
)
