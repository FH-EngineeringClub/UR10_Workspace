"""
This script is used to control the UR10 robot to play chess against the Stockfish chess engine.
"""

import platform
import subprocess
from time import sleep
import random
import socket
import json
import math
import rtde_io
import rtde_receive
import rtde_control
import chess
import chess.svg
import chess.engine
import chess.polyglot
from stockfish import Stockfish
from stockfish import StockfishException
from colorama import Fore

HOSTNAME = "192.168.2.81"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot
RTDE_FREQUENCY = 10  # Hz to update data from robot

rtde_io_ = rtde_io.RTDEIOInterface(HOSTNAME, RTDE_FREQUENCY)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(HOSTNAME, RTDE_FREQUENCY)
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)

ANGLE = 44.785  # angle between the robot base and the chess board (in degrees)
DX = 403.90  # Home TCP position relative to base (in mm)
DY = -571.83

BOARD_HEIGHT = (
    0.1229
    + 0.0025  # height of the board (in meters), measured as TCP Z relative to base
)
LIFT_HEIGHT = BOARD_HEIGHT + 0.254  # height of the lift (in meters)

TCP_RX = 2.7821  # rx (x rotation of TCP in radians)
TCP_RY = -1.465  # ry (y rotation of TCP in radians)
TCP_RZ = -0.0416  # rz (z rotation of TCP in radians)

BIN_POSITION = {"x": 202.8, "y": -254.93}  # position to move to when not in use

MOVE_SPEED = 1  # speed of the tool [m/s]
MOVE_ACCEL = 1  # acceleration of the tool [m/s^2]

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
    0,
    0,
    0,
]  # A 6d vector that defines which degrees of freedom are controlled by the force/torque sensor.
tcp_down = [
    0,
    0,
    -30,  # -0.1 newton force in negative z direction (onto the piece)
    0,
    0,
    0,
]  # The force vector [x, y, z, rx, ry, rz] in the force frame.
FORCE_TYPE = 2  # The type of force to apply
limits = [2, 2, 0.01, 1, 1, 1]  # The tcp speed limits [x, y, z, rx, ry, rz]

TCP_CONTACT = (
    control_interface.toolContact(  # this is not implemented correctly in python
        [0, 0, 1, 0, 0, 0]  # a workaround may be moveUntilContact
    )
)  # Check if the TCP is in contact with the piece

PIECE_HEIGHTS = {
    "k": 0.08049 - 0.003,
    "K": 0.08049 - 0.001,
    "p": 0.03345 + 0.002,  # add 2mm to the height of the pawn
    "P": 0.03345 + 0.002,  # add 2mm to the height of the pawn
    "r": 0.053 - 0.008,
    "R": 0.053 - 0.008,
    "n": 0.04569,
    "N": 0.04569,
    "b": 0.05902 - 0.002,
    "B": 0.05902 - 0.002,
    "q": 0.068 + 0.002,
    "Q": 0.068 + 0.002,
}  # dictionary to store the heights of the pieces in meters

stockfish_difficulty_level = {
    "easy": 600,
    "medium": 1500,
    "expert": 2100,
    "gm": 3500,
}  # dictionary to store the ELO difficulty levels of stockfish

osSystem = platform.system()  # Get the OS
if osSystem == "Darwin" or "Linux":
    stockfishPath = subprocess.run(
        ["which", "stockfish"], capture_output=True, text=True, check=True
    ).stdout.strip("\n")  # noqa: E501
elif osSystem == "Windows":
    stockfishPath = input("Please enter the full path to the stockfish executable:")
else:
    exit("No binary or executable found for stockfish")

zero_player_mode = input(
    Fore.LIGHTGREEN_EX
    + "Would you like to let stockfish play against itself? (no player input) (y/N)"
)

print(zero_player_mode)
if zero_player_mode == "y" or zero_player_mode == "Y":
    print(Fore.LIGHTMAGENTA_EX + "Entering zero player mode!")
    zero_player_mode = "TRUE"
else:
    print(Fore.GREEN + "Continuing with normal mode!")
    chess_vision_mode = input(
        Fore.LIGHTMAGENTA_EX
        + "Would you like to let the computer"
        + " detect human moves autonomously. (press space to"
        + " confirm human's move) (y/N)"
    )
    if chess_vision_mode.lower() == "y":
        print(Fore.GREEN + "Continuing with chess vision mode!")
        chess_vision_mode = True
    else:
        chess_vision_mode = False

start_new_game = input(
    Fore.YELLOW + "Would you like to continue the last saved game? (Y/n)"
)
if start_new_game != "y" and start_new_game != "Y" and start_new_game != "":
    board = chess.Board()  # Create a new board
    print(Fore.GREEN + "New game started!")
    print(board)
else:
    with open("lastgame.txt", "r", encoding="utf-8") as file:
        lastgame = file.read()
        board = chess.Board(lastgame)  # Load the last saved game
        print(board)
        print(Fore.GREEN + "Last game loaded!")


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
        MOVE_SPEED,  # speed: speed of the tool [m/s]
        MOVE_ACCEL,  # acceleration: acceleration of the tool [m/s^2]
    )


def forcemode_lower():
    """
    Lower the TCP to make contact with the piece
    """
    tcp_cycles = 0
    while TCP_CONTACT == 0 and tcp_cycles < 15:
        t_start = control_interface.initPeriod()
        # Move the robot down for 2 seconds
        tcp_cycles += 1
        print(tcp_cycles)
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


def lower_piece(move_instance):
    """
    Lower the piece to the board
    """
    robot_position = translate(move_instance.to_pos["x"], move_instance.to_pos["y"])
    if REMOVING_PIECE == 1:
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


def display_board():
    """
    Display the chess board by writing it to a SVG file.
    """
    with open(
        "chess.svg", "w", encoding="utf-8"
    ) as file_obj:  # Open a file to write to with explicit encoding
        file_obj.write(chess.svg.board(board))  # Write the board to the file


def save_last_play():
    """
    Save the last played game to a text file.
    """
    with open(
        "lastgame.txt", "w", encoding="utf-8"
    ) as file_obj:  # Open a file to write to with explicit encoding
        file_obj.write(board.fen())  # Write the board to the file


# Opening UR10 head positions JSON file
f = open("setup.json", encoding="utf-8")
data = json.load(f)


stockfish = Stockfish(path=stockfishPath)
stockfish.set_depth(8)  # How deep the AI looks
# stockfish.set_skill_level(20)  # Set the difficulty based skill level
# stockfish.set_elo_rating(1500)  # Set the difficulty based on elo rating
stockfish.get_parameters()  # Get all the parameters of stockfish

display_board()  # Display the board

if zero_player_mode == "TRUE":
    random_number = random.randint(2000, 3000)
    stockfish.set_elo_rating(random_number)
else:
    difficulty = input("Enter the difficulty level (easy, medium, expert, gm): ")
    if difficulty == "":
        difficulty = "easy"
        elo_rating = stockfish_difficulty_level.get(difficulty)
        stockfish.set_elo_rating(stockfish_difficulty_level.get(difficulty))
        print(
            Fore.GREEN + "Difficulty level set to",
            difficulty,
            "with ELO rating",
            elo_rating,
        )
    else:
        try:
            elo_rating = stockfish_difficulty_level.get(difficulty)
            stockfish.set_elo_rating(elo_rating)
            print(
                Fore.GREEN + "Difficulty level set to",
                difficulty,
                "with ELO rating",
                elo_rating,
            )
        except StockfishException:
            print(Fore.RED + "Invalid difficulty level")
            exit()


class Move:
    """
    Class to represent move of a piece from one position to another on the chess board
    """

    def __init__(
        self,
        piece_heights,
        current_board,
        position_data,
        current_move,
        board_height,
        lift_height,
    ):
        move_from = current_move[:2]  # from square
        move_to = current_move[-2:]  # to square
        print(move_from, move_to)
        from_position = position_data[move_from]
        to_position = position_data[move_to]
        from_piece_type = current_board.piece_at(chess.parse_square(move_from))
        to_piece_type = current_board.piece_at(chess.parse_square(move_to))
        print(from_piece_type, to_piece_type)
        if to_piece_type is None:
            to_piece_type = from_piece_type
        to_position_height = piece_heights[to_piece_type.symbol()]
        from_position_height = piece_heights[from_piece_type.symbol()]

        self.from_pos = from_position
        self.to_pos = to_position
        self.from_position_height = from_position_height
        self.to_position_height = to_position_height
        self.to_piece_type = to_piece_type
        self.move_from = move_from
        self.move_to = move_to
        self.board_height = board_height
        self.lift_height = lift_height

    def direct_move_piece(self):
        """
        Directly move a piece from one position to another on the chess board
        """
        print(
            "Moving piece",
            board.piece_at(origin_square),
            "from",
            self.move_from,
            "to",
            self.move_to,
        )
        board_height = self.to_position_height + self.board_height
        move_to_square(self.from_pos, self.lift_height)
        print(Fore.LIGHTBLUE_EX + "Energizing electromagnet...")
        send_command_to_robot(OUTPUT_24)  # energize the electromagnet
        move_to_square(self.from_pos, board_height)
        print(Fore.CYAN + "Lowering TCP...")
        sleep(0.2)
        forcemode_lower()
        print(Fore.CYAN + "Lifting piece...")
        lift_piece(self.from_pos)
        print("Moving piece to", self.move_to)
        move_to_square(self.to_pos, self.lift_height)
        print("Lowering piece...")
        lower_piece(self)
        print(Fore.LIGHTBLUE_EX + "De-energizing electromagnet...")
        send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
        sleep(1)
        move_to_square(self.to_pos, self.lift_height)
        print(Fore.CYAN + "Piece moved successfully!")

    def remove_piece(self):
        """
        Remove a piece from the chess board
        """
        board_height = self.to_position_height + self.board_height
        print("Removing piece", board.piece_at(target_square), "from", self.move_from)
        move_to_square(self.from_pos, self.lift_height)
        print(Fore.LIGHTBLUE_EX + "Energizing electromagnet...")
        send_command_to_robot(OUTPUT_24)  # energize the electromagnet
        move_to_square(self.from_pos, board_height)
        print(Fore.CYAN + "Lowering TCP...")
        sleep(0.2)
        forcemode_lower()
        print(Fore.CYAN + "Lifting piece...")
        move_to_square(self.from_pos, self.lift_height)
        lift_piece(self.from_pos)
        print("Moving piece to ex")
        move_to_square(BIN_POSITION, self.lift_height)  # move to the side position
        print(Fore.LIGHTBLUE_EX + "De-energizing electromagnet...")
        send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
        move_to_square(BIN_POSITION, self.lift_height)
        move_to_square(BIN_POSITION, self.lift_height)
        print(Fore.CYAN + "Piece removed successfully!")


while not board.is_game_over():
    if zero_player_mode == "TRUE":
        move_to_square(BIN_POSITION, LIFT_HEIGHT)  # move to the side position
        print(Fore.CYAN + "Moving to bin position...")
        display_board()  # Update the board svg

        save_last_play()  # Save the last played move

        stockfish.set_fen_position(board.fen())  # Set the position of the board
        bestMove = stockfish.get_top_moves(1)  # Get the best move
        uci_format_bestMove = chess.Move.from_uci(bestMove[0]["Move"])
        target_square = uci_format_bestMove.to_square
        origin_square = uci_format_bestMove.from_square
        if board.is_kingside_castling(uci_format_bestMove):
            print("Stockfish is castling kingside")
            if board.turn == chess.WHITE:
                move = "e1g1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "e8g8"  # e.g. "e2e4" or "e7e5"
            REMOVING_PIECE = 0
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.direct_move_piece()
            if board.turn == chess.WHITE:
                move = "h1f1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "h8f8"  # e.g. "e2e4" or "e7e5"
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.direct_move_piece()
            save_last_play()  # Save the last played move
        elif board.is_queenside_castling(uci_format_bestMove):
            print("Stockfish is castling queenside")
            if board.turn == chess.WHITE:
                move = "e1c1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "e8c8"  # e.g. "e2e4" or "e7e5"
            REMOVING_PIECE = 0
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.direct_move_piece()
            if board.turn == chess.WHITE:
                move = "a1d1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "a8d8"  # e.g. "e2e4" or "e7e5"
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.direct_move_piece()
            save_last_play()  # Save the last played move

        else:
            print("Stockfish is not castling")

            if board.piece_at(target_square) is None:
                print(Fore.CYAN + "Space not occupied")
                REMOVING_PIECE = 0

                move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )
                move_pos.direct_move_piece()
                save_last_play()  # Save the last played move

            else:
                print(
                    Fore.CYAN + "Space occupied by",
                    board.piece_at(target_square),
                    "removing piece...",
                )
                REMOVING_PIECE = 1

                move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )
                move_pos.remove_piece()
                move_pos.direct_move_piece()
                save_last_play()  # Save the last played move

        print(
            Fore.GREEN + "Stockfish moves:", board.push_san(bestMove[0]["Move"])
        )  # Push the best move to the board

        display_board()  # Update the board svg

        save_last_play()  # Save the last played move

    else:
        if board.turn == chess.WHITE:
            print(Fore.WHITE + "White to move")
        else:
            print(Fore.YELLOW + "Robot is on wrong side, skipping turn")
            board.push_san("0000")  # Push a blank move to the board
            save_last_play()  # Save the last played move
            continue
        move_to_square(BIN_POSITION, LIFT_HEIGHT)  # move to the side position
        print(Fore.CYAN + "Moving to bin position...")

        print(Fore.WHITE + "Legal moves:")

        for move in (
            board.legal_moves
        ):  # Print all the legal moves, including castling, en passant, and captures
            if board.is_castling(move):
                print(Fore.LIGHTRED_EX + "Castling " + move.uci(), end=" ")
            elif board.is_en_passant(move):
                print(Fore.LIGHTRED_EX + "En Passant " + move.uci(), end=" ")
            elif board.is_capture(move):
                print(Fore.LIGHTCYAN_EX + "Capture " + move.uci(), end=" ")
            else:
                print(Fore.WHITE + move.uci(), end=" ")

        if chess_vision_mode:
            print("In chess vision mode. Press space to blablabla.")
            space_detected = False

            while not space_detected:
                user_input = input()
                if input == " ":
                    print("continuing goo goo ga ga.")
                    space_detected = True
                else:
                    print("Please enter a space to continue.")
        else:
            inputmove = input(
                "\n"
                + Fore.BLUE
                + "Input move from the following legal moves, or 'undo' to undo (SAN format):"
            )  # Get the move from the user

            user_confirmation = input(
                Fore.YELLOW + "Are you sure you want to make this move? (Y/n)"
            )
            if (
                user_confirmation != "y"
                and user_confirmation != "Y"
                and user_confirmation != ""
            ):
                print(
                    Fore.RED + "Move not confirmed, please try again"
                )  # If the user doesn't confirm the move, ask for a new move
                continue  # Skip the rest of the loop and start from the beginning

            if inputmove == "undo":
                print("Undoing last move...")
                try:
                    for _ in range(2):
                        board.pop()
                except IndexError:
                    print(Fore.RED + "No moves to undo")
                display_board()
                save_last_play()
                continue
            else:
                try:
                    valid_input = (
                        chess.Move.from_uci(inputmove) in board.legal_moves
                    )  # Check if the move is valid
                except ValueError:
                    print(Fore.RED + "Move is not in SAN format. Please try again.")
                    continue

            if valid_input:
                board.push_san(inputmove)  # Push the move to the board

        # TODO: Add or statement for valid_detected_move
        if valid_input:
            display_board()  # Update the board svg

            stockfish.set_fen_position(board.fen())  # Set the position of the board
            bestMove = stockfish.get_top_moves(1)  # Get the best move
            uci_format_bestMove = chess.Move.from_uci(bestMove[0]["Move"])
            target_square = uci_format_bestMove.to_square
            origin_square = uci_format_bestMove.from_square
            if board.is_kingside_castling(uci_format_bestMove):
                print("Stockfish is castling kingside")
                if board.turn == chess.WHITE:
                    move = "e1g1"  # e.g. "e2e4" or "e7e5"
                else:
                    move = "e8g8"  # e.g. "e2e4" or "e7e5"
                REMOVING_PIECE = 0
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )

                move_pos.direct_move_piece()
                if board.turn == chess.WHITE:
                    move = "h1f1"  # e.g. "e2e4" or "e7e5"
                else:
                    move = "h8f8"  # e.g. "e2e4" or "e7e5"
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )

                move_pos.direct_move_piece()
                save_last_play()  # Save the last played move
            elif board.is_queenside_castling(uci_format_bestMove):
                print("Stockfish is castling queenside")
                if board.turn == chess.WHITE:
                    move = "e1c1"  # e.g. "e2e4" or "e7e5"
                else:
                    move = "e8c8"  # e.g. "e2e4" or "e7e5"
                REMOVING_PIECE = 0
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )
                move_pos.direct_move_piece()
                if board.turn == chess.WHITE:
                    move = "a1d1"  # e.g. "e2e4" or "e7e5"
                else:
                    move = "a8d8"  # e.g. "e2e4" or "e7e5"
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )
                move_pos.direct_move_piece()
                save_last_play()  # Save the last played move

            else:
                print("Stockfish is not castling")

                if board.piece_at(target_square) is None:
                    print(Fore.CYAN + "Space not occupied")
                    REMOVING_PIECE = 0

                    move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
                    move_pos = Move(
                        PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                    )
                    move_pos.direct_move_piece()
                    save_last_play()  # Save the last played move

                else:
                    print(
                        Fore.CYAN + "Space occupied by",
                        board.piece_at(target_square),
                        "removing piece...",
                    )
                    REMOVING_PIECE = 1

                    move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
                    move_pos = Move(
                        PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                    )
                    move_pos.remove_piece()
                    move_pos.direct_move_piece()
                    save_last_play()  # Save the last played move

            print(
                Fore.GREEN + "Stockfish moves:", board.push_san(bestMove[0]["Move"])
            )  # Push the best move to the board

            display_board()  # Update the board svg

            save_last_play()  # Save the last played move
        else:
            print(Fore.RED + "Not a legal move, Please try again")


move_to_square(BIN_POSITION, LIFT_HEIGHT)  # move to the side position
print(Fore.CYAN + "Moving to bin position...")

print(board.outcome())  # Print the winner of the game
print(Fore.GREEN + "Game over!")
