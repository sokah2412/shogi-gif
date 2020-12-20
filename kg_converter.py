import os
import argparse
import shogi.KIF
from helpers.matplotlibprinter import *
from helpers.board import *

RESCALE_FACTOR = 0.5

def generate_gif(kifu_file, rescale=RESCALE_FACTOR):
    kif = shogi.KIF.Parser.parse_file(kifu_file)[0]
    players = kif['names'][shogi.BLACK], kif['names'][shogi.WHITE]
    board_str = ['LNSGKGSNL', 'VBVVVVVRV', 'PPPPPPPPP']

    printer = MatPlotLibPrinter(players=players, size_factor=rescale)
    board = Board(board_str, board_str)

    dir_name, file_name = os.path.split(kifu_file)
    gif_name = file_name.split('.')[0] + '.gif'
    gif_path = os.path.join(dir_name, gif_name)

    moves = [Move(m) for m in kif['moves']]
    board.save(gif_path, printer, moves)

    return gif_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a GIF animation from a kifu file.')
    parser.add_argument('kifu_file', help="Kifu file to transform, must have '.kifu' extension")
    parser.add_argument('gif_name', help="Produced gif name")
    parser.add_argument('-r', '--rescale', default=RESCALE_FACTOR,
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
