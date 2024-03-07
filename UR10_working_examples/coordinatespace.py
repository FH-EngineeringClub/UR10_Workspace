from time import sleep
import socket
import json
import math
import rtde_io
import rtde_receive
import rtde_control

HOSTNAME = "192.168.2.81"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot

rtde_io_ = rtde_io.RTDEIOInterface(HOSTNAME)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(HOSTNAME)
control_interface = rtde_control.RTDEControlInterface(HOSTNAME)

ANGLE = 44.785  # angle between the robot base and the chess board (in degrees)
DX = 611.63  # Home TCP position relative to base (in mm)
DY = -354.83

BOARD_HEIGHT = 0.099  # height for the electromagnet to attach to pieces (in meters), measured as TCP Z relative to base
LIFT_HEIGHT = 0.40  # height of the lift (in meters)

TCP_RX = 0.20  # rx (x rotation of TCP in radians)
TCP_RY = -3.111  # ry (y rotation of TCP in radians)
TCP_RZ = -0.036  # rz (z rotation of TCP in radians)


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


def send_command_to_robot(command):
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


# direct_move_piece(from_position, to_position, BOARD_HEIGHT, LIFT_HEIGHT)
print(OUTPUT_0)
