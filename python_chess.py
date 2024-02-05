import chess
import chess.svg
from stockfish import Stockfish

stockfish = Stockfish(path="/usr/local/Cellar/stockfish/16/bin/stockfish")
stockfish.set_depth(20) #How deep the AI looks
stockfish.set_skill_level(20) #Highest rank stockfish
stockfish.get_parameters() #Get all the parameters

board = chess.Board() #Create a new board

def display_board():
    f = open("chess.svg", "w") # Open a file to write to
    f.write(chess.svg.board(board)) # Write the board to the file
    f.close() # Close the file

display_board() #Display the board

while not board.is_game_over():
    inputmove = input("Input move (SAN format):") #Get the move from the user
    board.push_san(inputmove) #Push the move to the board

    display_board() #Display the board

    stockfish.set_fen_position(board.fen()) #Set the position of the board
    bestMove = stockfish.get_top_moves(1) #Get the best move
    board.push_san(bestMove[0]['Move']) #Push the best move to the board
    
    display_board() #Display the board


print(board.outcome().winner)