"""
import python-chess and stockfish to play chess
"""

import platform
import subprocess
import chess
import chess.svg
from stockfish import Stockfish
from colorama import Fore

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


def display_board():
    """
    Display the chess board by writing it to a SVG file.
    """
    with open(
        "chess.svg", "w", encoding="utf-8"
    ) as f:  # Open a file to write to with explicit encoding
        f.write(chess.svg.board(board))  # Write the board to the file


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
        print(
            Fore.GREEN + "Stockfish moves:", board.push_san(bestMove[0]["Move"])
        )  # Push the best move to the board
        display_board()  # Display the board

    else:
        print(Fore.RED + "Not a legal move, Please try again")

print(board.outcome())  # Print the winner of the game
