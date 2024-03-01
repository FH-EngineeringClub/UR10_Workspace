import json
import math
import rtde_io
import rtde_receive
import rtde_control

rtde_io_ = rtde_io.RTDEIOInterface("192.168.2.81")
rtde_receive_ = rtde_receive.RTDEReceiveInterface("192.168.2.81")
control_interface = rtde_control.RTDEControlInterface("192.168.2.81")

ANGLE = 45  # angle between the robot base and the chess board (in degrees)
DX = 210  # Home TCP position relative to base (in mm)
DY = -405

BOARD_HEIGHT = 0.221  # height for the electromagnet to attach to pieces (in meters), measured as TCP Z relative to base
LIFT_HEIGHT = 0.40  # height of the lift (in meters)

TCP_RX = 0.03  # rx (x rotation of TCP in radians)
TCP_RY = -3.1347  # ry (y rotation of TCP in radians)
TCP_RZ = -0.041  # rz (z rotation of TCP in radians)


def translate(x, y):
    """
    Rotate a point by a given angle in a 2d space
    """
    x1 = x * math.cos(ANGLE) - y * math.sin(ANGLE)
    y1 = x * math.sin(ANGLE) + y * math.cos(ANGLE)
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
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


def lift_piece(pos):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            LIFT_HEIGHT,  # z (height to lift piece)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


def lower_piece(pos):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            BOARD_HEIGHT,  # z (height to lift piece)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


# Opening JSON file
f = open("UR10_working_examples/setup.json", encoding="utf-8")
data = json.load(f)

move = input("Enter move (SAN format): ")  # e.g. "e2e4" or "e7e5"
move_from = move[:2]  # from square
move_to = move[-2:]  # to square
from_position = data[move_from]
to_position = data[move_to]


def direct_move_piece():
    move_to_square(from_position, BOARD_HEIGHT)
    rtde_io_.setToolDigitalOut(0, True)  # energize the electromagnet
    lift_piece(from_position)
    move_to_square(to_position, LIFT_HEIGHT)
    lower_piece(to_position)
    rtde_io_.setToolDigitalOut(0, False)  # de-energize the electromagnet


direct_move_piece()
