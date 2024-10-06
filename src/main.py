"""
This script is used to control the UR10 robot to play chess against the Stockfish chess engine.
"""

import platform
import subprocess
from time import sleep
import random
import json
import chess
import chess.svg
import chess.engine
from stockfish import Stockfish
from stockfish import StockfishException
from colorama import Fore
import threading
from button_input import connectToButton, listenForButton
import yaml
from robot_api.api import (
    move_to_square,
    forcemode_lower,
    lift_piece,
    lower_piece,
    send_command_to_robot,
    OUTPUT_24,
    OUTPUT_0,
    disconnect_from_robot,
    direct_move_piece,
    remove_piece,
)

# Load configuration from config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)


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

# Piece Heights
PIECE_HEIGHTS = config["piece_heights"]

# Stockfish Difficulty Levels
stockfish_difficulty_level = config["stockfish_difficulty_level"]


osSystem = platform.system()  # Get the OS
if osSystem == "Darwin" or osSystem == "Linux":
    stockfishPath = subprocess.run(
        ["which", "stockfish"], capture_output=True, text=True, check=True
    ).stdout.strip("\n")  # noqa: E501
elif osSystem == "Windows":
    stockfishPath = subprocess.run(
        ["where", "stockfish"], capture_output=True, text=True
    )
    stockfishPath = stockfishPath.stdout.strip()
else:
    exit("No binary or executable found for stockfish")

zero_player_mode = input(
    Fore.LIGHTGREEN_EX
    + "Would you like to let stockfish play against itself? (no player input) (y/N)"
)

if zero_player_mode.lower() == "y":
    print(Fore.LIGHTMAGENTA_EX + "Entering zero player mode!")
    zero_player_mode = "TRUE"
    chess_vision_mode = False  # No need for vision in zero-player mode
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

        # Import ChessViz only if chess vision mode is enabled
        from vision.chessviz import ChessViz

        chessviz = ChessViz(
            config["vision"]["board_corners"][0],
            config["vision"]["board_corners"][1],
            cam_index=config["vision"]["cam_index"],
        )

        # Initialize vision thread and lock
        sample_size = config["vision"]["sample_size"]
        vision_thread = threading.Thread(
            target=chessviz.chess_array_update_thread, args=(sample_size,)
        )
        vision_thread.start()
        lock = threading.Lock()
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
    try:
        with open("lastgame.txt", "r", encoding="utf-8") as file:
            lastgame = file.read()
            board = chess.Board(lastgame)  # Load the last saved game
            print(board)
            print(Fore.GREEN + "Last game loaded!")
    except FileNotFoundError:
        board = chess.Board()
        print(Fore.RED + "No last game found, starting new game!")
        print(board)


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
with open("setup.json", encoding="utf-8") as f:
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

    def main_direct_move_piece(self):
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
        direct_move_piece(self, REMOVING_PIECE)

    def main_remove_piece(self):
        """
        Remove a piece from the chess board
        """
        remove_piece(self, board, origin_square)


# converts 2d array in san format to concise fen(cfen), i.e. a fen without values
# for player turn, castling rights, etc.
def convert_to_cfen(chess_array):
    rows = []
    for i in range(7, -1, -1):
        row = ""
        empty_count = 0
        for j in range(8):
            piece = chess_array[i][j]
            if piece == ".":
                empty_count += 1
            else:
                if empty_count > 0:
                    row += str(empty_count)
                    empty_count = 0
                row += piece

        if empty_count > 0:
            row += str(empty_count)
        rows.append(row)

    cfen = "/".join(rows)
    return cfen


def update_board_with_vision(chess_array, board):
    new_fen = convert_to_cfen(chess_array)
    print("new fen: ", new_fen)

    for move in board.legal_moves:
        board.push(move)
        print("exisiting fen: ", board.fen().split(" ")[0])
        if new_fen == board.fen().split(" ")[0]:
            return True
        board.pop()

    return False


if chess_vision_mode:
    sample_size = 20
    vision_thread = threading.Thread(
        target=chessviz.chess_array_update_thread, args=(sample_size,)
    )
    vision_thread.start()
    lock = threading.Lock()


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
            move_pos.main_direct_move_piece()
            if board.turn == chess.WHITE:
                move = "h1f1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "h8f8"  # e.g. "e2e4" or "e7e5"
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.main_direct_move_piece()
            save_last_play()  # Save the last played move
        elif board.is_queenside_castling(uci_format_bestMove):
            print("Stockfish is castling queenside")
            if board.turn == chess.WHITE:
                move = "e1c1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "e8c8"  # e.g. "e2e4" or "e7e5"
            REMOVING_PIECE = 0
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.main_direct_move_piece()
            if board.turn == chess.WHITE:
                move = "a1d1"  # e.g. "e2e4" or "e7e5"
            else:
                move = "a8d8"  # e.g. "e2e4" or "e7e5"
            move_pos = Move(PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT)
            move_pos.main_direct_move_piece()
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
                move_pos.main_direct_move_piece()
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
                move_pos.main_remove_piece()
                move_pos.main_direct_move_piece()
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
            while True:
                print("\n", "Press enter key to register move.")
                connectToButton()
                listenForButton()

                chessviz.counter_on.clear()
                chessviz.counter_on.wait()

                with lock:
                    chess_array = chessviz.chess_array
                    print(chess_array)

                valid_input = update_board_with_vision(chess_array, board)

                if valid_input:
                    break

                print("Illegal move, please try again.")
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

                move_pos.main_direct_move_piece()
                if board.turn == chess.WHITE:
                    move = "h1f1"  # e.g. "e2e4" or "e7e5"
                else:
                    move = "h8f8"  # e.g. "e2e4" or "e7e5"
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )

                move_pos.main_direct_move_piece()
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
                move_pos.main_direct_move_piece()
                if board.turn == chess.WHITE:
                    move = "a1d1"  # e.g. "e2e4" or "e7e5"
                else:
                    move = "a8d8"  # e.g. "e2e4" or "e7e5"
                move_pos = Move(
                    PIECE_HEIGHTS, board, data, move, BOARD_HEIGHT, LIFT_HEIGHT
                )
                move_pos.main_direct_move_piece()
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
                    move_pos.main_direct_move_piece()
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
                    move_pos.main_remove_piece()
                    move_pos.main_direct_move_piece()
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

disconnect_from_robot()
