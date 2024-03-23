"""
import python-chess and stockfish to play chess
"""

import platform
import subprocess
import chess
import chess.svg
from stockfish import Stockfish
from colorama import Fore

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

stockfish = Stockfish(path=stockfishPath)
stockfish.set_depth(20)  # How deep the AI looks
# stockfish.set_skill_level(20)  # Set the difficulty based skill level (mutually exclusive with elo rating)
# stockfish.set_elo_rating(1500)  # Set the difficulty based on elo rating
stockfish.get_parameters()  # Get all the parameters of stockfish

board = chess.Board()  # Create a new board

difficulty = input("Enter the difficulty level (easy, medium, expert, gm): ")
elo_rating = stockfish_difficulty_level.get(difficulty)
if elo_rating is None:
    print("Invalid difficulty level")
    exit()
stockfish.set_elo_rating(elo_rating)
print(Fore.GREEN + "Difficulty level set to", difficulty, "with ELO rating", elo_rating)


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
        Fore.BLUE + "Input move from the following legal moves (SAN format):"
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

    try:
        board.parse_san(inputmove)
    except ValueError:
        print(Fore.RED + "Move is not in SAN format. Please try again.")
        continue

    valid_move = (
        chess.Move.from_uci(inputmove) in board.pseudo_legal_moves
    )  # Check if the move is valid

    if valid_move is True:
        board.push_san(inputmove)  # Push the move to the board

        display_board()  # Display the board

        stockfish.set_fen_position(board.fen())  # Set the position of the board
        bestMove = stockfish.get_top_moves(1)  # Get the best move
        target_square = chess.Move.from_uci(bestMove[0]["Move"]).to_square
        origin_square = chess.Move.from_uci(bestMove[0]["Move"]).from_square

        if board.piece_at(target_square) is None:
            print(Fore.CYAN + "Space not occupied")
            REMOVING_PIECE = 0

            move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
            move_from = move[:2]  # from square
            move_to = move[-2:]  # to square
            print(move_from, move_to)
            from_piece_type = board.piece_at(chess.parse_square(move_from))
            to_piece_type = board.piece_at(chess.parse_square(move_to))

        else:
            print(
                Fore.CYAN + "Space occupied by",
                board.piece_at(target_square),
                "removing piece...",
            )
            REMOVING_PIECE = 1

            move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
            move_from = move[:2]  # from square
            move_to = move[-2:]  # to square
            print(move_from, move_to)
            from_piece_type = board.piece_at(chess.parse_square(move_from))
            to_piece_type = board.piece_at(chess.parse_square(move_to))

        print(
            Fore.GREEN + "Stockfish moves:", board.push_san(bestMove[0]["Move"])
        )  # Push the best move to the board

        display_board()  # Update the board svg
    else:
        print(Fore.RED + "Not a legal move, Please try again")

print(Fore.CYAN + "Moving to bin position...")

print(board.outcome())  # Print the winner of the game
print(Fore.GREEN + "Game over!")
