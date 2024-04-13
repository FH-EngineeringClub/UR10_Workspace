import math
import rtde_control
import rtde_receive
from colorama import Fore

HOSTNAME = "192.168.2.81"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot
RTDE_FREQUENCY = 10  # Hz to update from robot
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)
receive_interface = rtde_receive.RTDEReceiveInterface(HOSTNAME, RTDE_FREQUENCY)


ANGLE = 44.785  # angle between the robot base and the chess board (in degrees)
DX = 401.34  # Home TCP position relative to base (in mm)
DY = -564.75

BOARD_HEIGHT = (
    0.09375
    + 0.03  # height of the board (in meters), measured as TCP Z relative to base
)
LIFT_HEIGHT = BOARD_HEIGHT + 0.254  # height of the lift (in meters)

TCP_RX = 2.2226  # rx (x rotation of TCP in radians)
TCP_RY = -2.2413  # ry (y rotation of TCP in radians)
TCP_RZ = 0.0489  # rz (z rotation of TCP in radians)

BIN_POSITION = {"x": 202.8, "y": -354.93}  # position to move to when not in use

MOVE_SPEED = 0.5  # speed of the tool [m/s]
MOVE_ACCEL = 0.3  # acceleration of the tool [m/s^2]

FORCE_SECONDS = 2  # duration of the force mode in seconds

task_frame = [
    0,
    0,
    0,
    0,
    0,
    0,
]  # A pose vector that defines the force frame relative to the base frame.
selection_vector = [
    0,
    0,
    1,
    1,
    1,
    1,
]  # A 6d vector that defines which degrees of freedom are controlled by the force/torque sensor.
tcp_down = [
    0,
    0,
    -30,
    0,
    0,
    0,
]  # The force vector [x, y, z, rx, ry, rz] in the force frame.
FORCE_TYPE = 3  # The type of force to apply
limits = [2, 2, 1.5, 1, 1, 1]  # The tcp speed limits [x, y, z, rx, ry, rz]


def translate(x, y):
    """
    Rotate a point by a given angle in a 2d space
    """
    x1 = y * math.cos(ANGLE) - x * math.sin(ANGLE)
    y1 = y * math.sin(ANGLE) + x * math.cos(ANGLE)
    return x1 + DX, y1 + DY


def move_to_square(pos, height):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            height,  # z (height of the chess board)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        MOVE_SPEED,  # speed: speed of the tool [m/s]
        MOVE_ACCEL,  # acceleration: acceleration of the tool [m/s^2]
    )


TCP_CONTACT = (
    control_interface.toolContact(  # this is not implemented correctly in python
        [0, 0, 1, 0, 0, 0]  # a workaround may be moveUntilContact
    )
)  # Check if the TCP is in contact with the piece


def forcemode_lower():
    """
    Lower the TCP to make contact with the piece
    """
    tcp_cycles = 0
    while TCP_CONTACT == 0 and tcp_cycles < 150:
        t_start = control_interface.initPeriod()
        # Move the robot down for 2 seconds
        tcp_cycles += 1
        print(tcp_cycles)
        control_interface.forceMode(
            task_frame, selection_vector, tcp_down, FORCE_TYPE, limits
        )
        control_interface.waitPeriod(t_start)
    if tcp_cycles == 150:
        print(Fore.RED + "TCP was not able to find the piece")
    control_interface.forceModeStop()


move_to_square({"x": -100, "y": 0}, BOARD_HEIGHT + 0.20)

forcemode_lower()

# print(dir(control_interface))


# control_interface.moveUntilContact(
#     [
#         1,
#         1,
#         1,
#         1,
#         0,
#         0,
#     ],  # xd: tool speed [m/s] (spatial vector)
#     [
#         0,
#         0,
#         0,
#         0,
#         0,
#         0,
#     ],  # direction: List of six floats. The first three elements are interpreted as a 3D vector
#     # (in the robot base coordinate system) giving the direction in which contacts should be detected.
#     # If all elements of the list are zero, contacts from all directions are considered.
#     # You can also set direction=get_target_tcp_speed() in which case it will detect contacts
#     # in the direction of the TCP movement.
#     #
#     1.2,  # acceleration: tool position acceleration [m/s^2]
# )

# # forcemode_lower()
