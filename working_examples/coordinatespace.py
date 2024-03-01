import json
import math
import rtde_io
import rtde_receive
import rtde_control

rtde_io_ = rtde_io.RTDEIOInterface("192.168.56.101")
rtde_receive_ = rtde_receive.RTDEReceiveInterface("192.168.56.101")
control_interface = rtde_control.RTDEControlInterface("192.168.56.101")

ANGLE = 45  # angle between the robot base and the chess board (in degrees)
DX = -380  # Home TCP position relative to base (in mm)
DY = -500
BOARD_HEIGHT = 0.20  # height for the electromagnet to attach to pieces (in meters)
LIFT_HEIGHT = 0.40  # height of the lift (in meters)


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
            0.546,  # rx (x rotation of TCP in radians)
            3.062,  # ry (y rotation of TCP in radians)
            0.045,  # rz (z rotation of TCP in radians)
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
            0.546,  # rx (x rotation of TCP in radians)
            3.062,  # ry (y rotation of TCP in radians)
            0.045,  # rz (z rotation of TCP in radians)
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
            0.546,  # rx (x rotation of TCP in radians)
            3.062,  # ry (y rotation of TCP in radians)
            0.045,  # rz (z rotation of TCP in radians)
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


# Opening JSON file
f = open("setup.json", encoding="utf-8")
data = json.load(f)

move = input("Enter move (SAN format): ")  # e.g. "e2e4" or "e7e5"
move_from = move[:2]  # from square
move_to = move[-2:]  # to square
from_position = data[move_from]
to_position = data[move_to]

move_to_square(from_position, BOARD_HEIGHT)
rtde_io_.setToolDigitalOut(0, True)  # energize the electromagnet
lift_piece(from_position)
move_to_square(to_position, LIFT_HEIGHT)
lower_piece(to_position)
rtde_io_.setToolDigitalOut(0, False)  # de-energize the electromagnet
