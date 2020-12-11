import argparse
import shogi.KIF
from helpers.matplotlibprinter import *
from helpers.board import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a GIF animation from a kifu file.')
    parser.add_argument('kifu_file', help="Kifu file to transform, must have '.kifu' extension")
    parser.add_argument('gif_name', help="Produced gif name")
    parser.add_argument('-r', '--rescale', default=0.5,
                        help="Size factor to rescale gif (default: 0.5 to minimize RAM usage)",
                        type=int)

    args = parser.parse_args()

    if not args.kifu_file.endswith('.kifu'):
        parser.print_usage()
        print('Please upload a kif encoded file, with extension .kifu')
        exit()

    kif = shogi.KIF.Parser.parse_file(args.kifu_file)[0]
    if len(kif['moves']) == 0:
        print('Error occurs when reading kifu file')
        exit()
    players = kif['names'][shogi.BLACK], kif['names'][shogi.WHITE]
    board_str = ['LNSGKGSNL', 'VBVVVVVRV', 'PPPPPPPPP']

    printer = MatPlotLibPrinter(players=players, size_factor=args.rescale)
    board = Board(board_str, board_str)

    moves = [Move(m) for m in kif['moves']]
    board.save(args.gif_name, printer, moves)
