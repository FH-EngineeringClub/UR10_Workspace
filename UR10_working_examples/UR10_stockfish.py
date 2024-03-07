"""
import python-chess and stockfish to play chess
"""

import platform
import subprocess
from time import sleep
import socket
import json
import math
import rtde_io
import rtde_receive
import rtde_control
import chess
import chess.svg
from stockfish import Stockfish
from colorama import Fore

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

osSystem = platform.system()  # Get the OS
if osSystem == "Darwin" or "Linux":
    stockfishPath = subprocess.run(
        ["which", "stockfish"], capture_output=True, text=True, check=True
    ).stdout.strip("\n")  # noqa: E501
elif osSystem == "Windows":
    stockfishPath = input("Please enter the full path to the stockfish executable:")
else:
    exit("No binary or executable found for stockfish")

stockfish = Stockfish(path=stockfishPath)
stockfish.set_depth(20)  # How deep the AI looks
stockfish.set_skill_level(20)  # Highest rank stockfish
stockfish.get_parameters()  # Get all the parameters

board = chess.Board()  # Create a new board


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


def display_board():
    """
    Display the chess board by writing it to a SVG file.
    """
    with open(
        "chess.svg", "w", encoding="utf-8"
    ) as file_obj:  # Open a file to write to with explicit encoding
        file_obj.write(chess.svg.board(board))  # Write the board to the file


# Opening UR10 head positions JSON file
f = open("setup.json", encoding="utf-8")
data = json.load(f)


def direct_move_piece(from_pos, to_pos, board_height, lift_height):
    print("Moving piece from", move_from, "to", move_to)
    move_to_square(from_pos, board_height)
    print("Energizing electromagnet...")
    send_command_to_robot(OUTPUT_24)  # energize the electromagnet
    print("Lifting piece...")
    lift_piece(from_pos)
    print("Moving piece to", move_to)
    if (
        move_to == "ex"
    ):  # TODO rename move_to ex in this case to some other variable (currently causes "string indices must be integers" error)
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


display_board()  # Display the board

while not board.is_game_over():
    print(Fore.WHITE + "Legal moves:", [move.uci() for move in board.legal_moves])
    inputmove = input(
        "Input move from the following legal moves (SAN format):"
    )  # Get the move from the user

    user_confirmation = input("Are you sure you want to make this move? (y/n)")
    if user_confirmation != "y":
        print(
            Fore.RED + "Move not confirmed, please try again"
        )  # If the user doesn't confirm the move, ask for a new move
        continue  # Skip the rest of the loop and start from the beginning

    valid_move = (
        chess.Move.from_uci(inputmove) in board.legal_moves
    )  # Check if the move is valid

    if valid_move is True:
        board.push_san(inputmove)  # Push the move to the board

        display_board()  # Display the board

        stockfish.set_fen_position(board.fen())  # Set the position of the board
        bestMove = stockfish.get_top_moves(1)  # Get the best move
        target_square = chess.Move.from_uci(bestMove[0]["Move"]).to_square

        if board.piece_at(target_square) is None:
            print(Fore.CYAN + "Space not occupied")

            move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
            move_from = move[:2]  # from square
            move_to = move[-2:]  # to square
            print(move_from, move_to)
            from_position = data[move_from]
            to_position = data[move_to]
            direct_move_piece(from_position, to_position, BOARD_HEIGHT, LIFT_HEIGHT)

        else:
            print(
                Fore.CYAN + "Space occupied by",
                board.piece_at(target_square),
                "removing piece...",
            )

            move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
            move_from = move[:2]  # from square
            move_to = move[-2:]  # to square
            print(move_from, move_to)
            from_position = data[move_from]
            to_position = "ex"
            direct_move_piece(from_position, to_position, BOARD_HEIGHT, LIFT_HEIGHT)

        print(
            Fore.GREEN + "Stockfish moves:", board.push_san(bestMove[0]["Move"])
        )  # Push the best move to the board

        display_board()  # Display the board

    else:
        print(Fore.RED + "Not a legal move, Please try again")

print(board.outcome())  # Print the winner of the game
