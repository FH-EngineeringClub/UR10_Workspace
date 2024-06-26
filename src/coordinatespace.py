"""
This file is to help with setting up the chess board before running the chess game.
Clear the chess board, and use this file to move the robot to each square on the board.
"""

from time import sleep
import socket
import json
import math
import rtde_io
import rtde_receive
import rtde_control

HOSTNAME = "192.168.2.81"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot
RTDE_FREQUENCY = 10.0  # Hz to update from robot

rtde_io_ = rtde_io.RTDEIOInterface(HOSTNAME, RTDE_FREQUENCY)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(HOSTNAME, RTDE_FREQUENCY)
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)

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


def translate(x, y):
    """
    Rotate a point by a given angle in a 2d space
    """
    x1 = y * math.cos(ANGLE) - x * math.sin(ANGLE)
    y1 = y * math.sin(ANGLE) + x * math.cos(ANGLE)
    return x1 + DX, y1 + DY


def move_to_square(pos, height):
    """
    Move the TCP to a given position on the chess board
    """
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
    """
    Lift the piece from the board
    """
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
    """
    Lower the piece to the board
    """
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


def send_command_to_robot(command):
    """
    Send a command to the robot directly using a socket connection
    """
    # Connect to the robot
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOSTNAME, HOST_PORT))

    # Send the command to the robot
    sock.send(bytes(command, "utf-8"))

    # Receive and print the response from the robot
    # response = sock.recv(1024)
    # print("Response from robot:", response)

    # Close the connection
    sock.close()
    sleep(0.2)  # Allow the piece to attach to the electromagnet


OUTPUT_24 = "sec myProg():\n\
    set_tool_voltage(24)\n\
end\n\
myProg()\n"

OUTPUT_0 = "sec myProg():\n\
    set_tool_voltage(0)\n\
end\n\
myProg()\n"

# Opening JSON file
f = open("setup.json", encoding="utf-8")
data = json.load(f)

move = input("Enter move (SAN format): ")  # e.g. "e2e4" or "e7e5"
move_from = move[:2]  # from square
move_to = move[-2:]  # to square
from_position = data[move_from]
to_position = data[move_to]


def direct_move_piece(from_pos, to_pos, board_height, lift_height):
    """
    Directly move a piece from one position to another on the chess board
    """
    print("Moving piece from", move_from, "to", move_to)
    move_to_square(from_pos, board_height)
    print("Energizing electromagnet...")
    send_command_to_robot(OUTPUT_24)  # energize the electromagnet
    print("Lifting piece...")
    lift_piece(from_pos)
    print("Moving piece to", move_to)
    if move_to == "ex":
        move_to_square(to_pos, lift_height)
        print("De-energizing electromagnet...")
        send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
        print("Piece removed successfully!")
    else:
        move_to_square(to_pos, lift_height)
        print("Lowering piece...")
        lower_piece(to_pos)
        print("De-energizing electromagnet...")
        send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
        print("Piece moved successfully!")


direct_move_piece(from_position, to_position, BOARD_HEIGHT, LIFT_HEIGHT)
# print(OUTPUT_0)

control_interface.stopScript()
