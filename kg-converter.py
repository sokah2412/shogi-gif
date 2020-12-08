import sys
import shogi.KIF
from helpers.matplotlibprinter import *
from helpers.board import *

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f'usage: python {sys.argv[0]} kifu_name gif_name')
        exit()

    kif = shogi.KIF.Parser.parse_file(sys.argv[1])[0]
    players = kif['names'][shogi.BLACK], kif['names'][shogi.WHITE]
    board_str = ['LNSGKGSNL', 'VBVVVVVRV', 'PPPPPPPPP']

    printer = MatPlotLibPrinter(players=players)
    board = Board(board_str, board_str)

    moves = [Move(m) for m in kif['moves']]
    board.save(sys.argv[2], printer, moves)
