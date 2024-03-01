import json
import math
import rtde_io
import rtde_receive
import rtde_control

rtde_io_ = rtde_io.RTDEIOInterface("192.168.56.101")
rtde_receive_ = rtde_receive.RTDEReceiveInterface("192.168.56.101")
control_interface = rtde_control.RTDEControlInterface("192.168.56.101")

ANGLE = 45  # angle between the robot base and the chess board
DX = -380  # Home TCP positon relative to base
DY = -500
BOARD_HEIGHT = 0.20  # height for the electromagnet to attach to pieces
LIFT_HEIGHT = 0.40  # height of the lift


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
            0.546,  # rx
            3.062,  # ry
            0.045,  # rz
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
            0.546,  # rx
            3.062,  # ry
            0.045,  # rz
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
            0.546,  # rx
            3.062,  # ry
            0.045,  # rz
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


# Opening JSON file
f = open("setup.json")
data = json.load(f)

move = input("Enter move: ")
move_from = move[:2]
move_to = move[-2:]
from_position = data[move_from]
to_position = data[move_to]

move_to_square(from_position, BOARD_HEIGHT)
rtde_io_.setToolDigitalOut(0, True)  # energize the electromagnet
lift_piece(from_position)
move_to_square(to_position, LIFT_HEIGHT)
lower_piece(to_position)
rtde_io_.setToolDigitalOut(0, False)  # de-energize the electromagnet
