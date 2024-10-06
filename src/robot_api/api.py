# Description: This file contains the API for the robot. It is responsible for the communication between the robot and the rest of the system.
from time import sleep
import socket
import math
import rtde_io
import rtde_receive
import rtde_control
from colorama import Fore
import yaml

# Load configuration from config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Robot Configuration
HOSTNAME = config["robot"]["hostname"]  # The IP address of your Universal Robot
HOST_PORT = config["robot"]["host_port"]  # The port to send commands to the robot
RTDE_FREQUENCY = config["robot"]["rtde_frequency"]  # Hz to update data from robot

# Robot Parameters
ANGLE = config["robot_parameters"]["angle"]
DX = config["robot_parameters"]["dx"]
DY = config["robot_parameters"]["dy"]
BOARD_HEIGHT = config["robot_parameters"]["board_height"]
BOARD_LIFT_HEIGHT = config["robot_parameters"]["board_lift_height"]
LIFT_HEIGHT = BOARD_LIFT_HEIGHT + BOARD_HEIGHT
TCP_RX = config["robot_parameters"]["tcp_rx"]
TCP_RY = config["robot_parameters"]["tcp_ry"]
TCP_RZ = config["robot_parameters"]["tcp_rz"]
BIN_POSITION = config["robot_parameters"]["bin_position"]
MOVE_SPEED = config["robot_parameters"]["move_speed"]
MOVE_ACCEL = config["robot_parameters"]["move_accel"]

# Force Control Parameters
FORCE_SECONDS = config["force_control"]["force_seconds"]
task_frame = config["force_control"]["task_frame"]
selection_vector = config["force_control"]["selection_vector"]
tcp_down = config["force_control"]["tcp_down"]
FORCE_TYPE = config["force_control"]["force_type"]
limits = config["force_control"]["limits"]

rtde_io_ = rtde_io.RTDEIOInterface(HOSTNAME, RTDE_FREQUENCY)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(HOSTNAME, RTDE_FREQUENCY)
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)


def translate(x, y):
    """
    Rotate a point by a given angle in a 2d space
    """
    x1 = y * math.cos(ANGLE) - x * math.sin(ANGLE)
    y1 = y * math.sin(ANGLE) + x * math.cos(ANGLE)
    return x1 + DX, y1 + DY


def move_to_square(pos, height=LIFT_HEIGHT):
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
    while TCP_CONTACT == 0 and tcp_cycles < 15:
        t_start = control_interface.initPeriod()
        # Move the robot down for 2 seconds
        tcp_cycles += 1
        control_interface.forceMode(
            task_frame, selection_vector, tcp_down, FORCE_TYPE, limits
        )
        control_interface.waitPeriod(t_start)
    if tcp_cycles == 20:
        print(Fore.RED + "TCP was not able to find the piece")
    control_interface.forceModeStop()


def lift_piece(pos):
    """
    Lift the piece from the board
    """
    robot_position = translate(pos["x"], pos["y"])
    sleep(0.5)
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            LIFT_HEIGHT,  # z (height to lift piece)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        MOVE_SPEED,  # speed: speed of the tool [m/s]
        MOVE_ACCEL,  # acceleration: acceleration of the tool [m/s^2]
    )
    sleep(0.5)


def lower_piece(move_instance, removing_piece):
    """
    Lower the piece to the board
    """
    robot_position = translate(move_instance.to_pos["x"], move_instance.to_pos["y"])
    if removing_piece == 1:
        control_interface.moveL(
            [
                robot_position[0] / 1000,  # x
                robot_position[1] / 1000,  # y
                move_instance.from_position_height
                + BOARD_HEIGHT,  # z (height to lift piece)
                TCP_RX,  # rx (x rotation of TCP in radians)
                TCP_RY,  # ry (y rotation of TCP in radians)
                TCP_RZ,  # rz (z rotation of TCP in radians)
            ],
            MOVE_SPEED,  # speed: speed of the tool [m/s]
            MOVE_ACCEL,  # acceleration: acceleration of the tool [m/s^2]
        )
    else:
        control_interface.moveL(
            [
                robot_position[0] / 1000,  # x
                robot_position[1] / 1000,  # y
                move_instance.to_position_height
                + BOARD_HEIGHT,  # z (height to lift piece)
                TCP_RX,  # rx (x rotation of TCP in radians)
                TCP_RY,  # ry (y rotation of TCP in radians)
                TCP_RZ,  # rz (z rotation of TCP in radians)
            ],
            MOVE_SPEED,  # speed: speed of the tool [m/s]
            MOVE_ACCEL,  # acceleration: acceleration of the tool [m/s^2]
        )
    sleep(0.5)


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
    sleep(0.5)  # Allow the piece to attach to the electromagnet


OUTPUT_24 = "sec myProg():\n\
    set_tool_voltage(24)\n\
end\n\
myProg()\n"


OUTPUT_0 = "sec myProg():\n\
    set_tool_voltage(0)\n\
end\n\
myProg()\n"


def disconnect_from_robot():
    """
    Disconnect from the robot
    """
    control_interface.stopScript()  # Disconnect from the robot


def direct_move_piece(move, removing_piece):
    board_height = move.from_position_height + BOARD_HEIGHT
    move_to_square(move.from_pos, LIFT_HEIGHT)
    print(Fore.LIGHTBLUE_EX + "Energizing electromagnet...")
    send_command_to_robot(OUTPUT_24)  # energize the electromagnet
    move_to_square(move.from_pos, board_height)
    print(Fore.CYAN + "Lowering TCP...")
    sleep(0.2)
    forcemode_lower()
    print(Fore.CYAN + "Lifting piece...")
    lift_piece(move.from_pos)
    print("Moving piece to", move.move_to)
    move_to_square(move.to_pos, LIFT_HEIGHT)
    print("Lowering piece...")
    lower_piece(move, removing_piece)
    print(Fore.LIGHTBLUE_EX + "De-energizing electromagnet...")
    send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
    sleep(1)
    move_to_square(move.to_pos, LIFT_HEIGHT)
    print(Fore.CYAN + "Piece moved successfully!")


def remove_piece(move, board, origin_square):
    board_height = move.to_position_height + BOARD_HEIGHT
    print("Removing piece", board.piece_at(origin_square), "from", move.move_to)
    move_to_square(move.to_pos, LIFT_HEIGHT)
    print(Fore.LIGHTBLUE_EX + "Energizing electromagnet...")
    send_command_to_robot(OUTPUT_24)  # energize the electromagnet
    move_to_square(move.to_pos, board_height)
    print(Fore.CYAN + "Lowering TCP...")
    sleep(0.2)
    forcemode_lower()
    print(Fore.CYAN + "Lifting piece...")
    move_to_square(move.to_pos, LIFT_HEIGHT)
    lift_piece(move.to_pos)
    print("Moving piece to ex")
    move_to_square(BIN_POSITION, LIFT_HEIGHT)  # move to the side position
    print(Fore.LIGHTBLUE_EX + "De-energizing electromagnet...")
    send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
    move_to_square(BIN_POSITION, LIFT_HEIGHT)
    move_to_square(BIN_POSITION, LIFT_HEIGHT)
    print(Fore.CYAN + "Piece removed successfully!")
