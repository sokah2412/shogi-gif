import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import enum
import sys
import shogi.KIF
from numpngw import AnimatedPNGWriter
from helpers.printer import *
from helpers.board import *

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f'usage: python {sys.argv[0]} kifu_name gif_name')
        exit()

    kif = shogi.KIF.Parser.parse_file(sys.argv[1])[0]
    players = kif['names'][shogi.BLACK], kif['names'][shogi.WHITE]
    board_str = ['LNSGKGSNL', 'VBVVVVVRV', 'PPPPPPPPP']

    canvas_width = 10
    canvas_height = 17

    plt.switch_backend('TKAgg') # Needed because QT4Agg yield weird error
    fig, ax = plt.subplots(figsize=(canvas_width, canvas_height))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    board = Board(board_str, board_str)
    printer = Printer(ax, board, canvas_width, canvas_height, players)

    def init_anim():
        ax.axis('off')
        printer.draw_frame()
        printer.draw_pieces()

    def update_anim(data):
        ax.clear()
        ax.axis('off')
        color, move_str = data
        winner = None
        if color[0] in ['e', 'f']:
            winner = 'black' if color[1] == 'b' else 'white'
            color = winner if color[0] == 'e' else color
        move = None
        if color[1] != 'i' and color[0] != 'f':
            color = Color[color]
            move = Move(move_str)
            board.move(color, move)
        printer.draw_frame(winner=winner, move=move)
        printer.draw_pieces()

    data = [('black', move) if i % 2 == 0 else ('white', move) for i,
            move in enumerate(kif['moves'])]
    data.insert(0, ('bi',''))
    data[-1] = ('eb', data[-1][1]) if data[-1][0] == 'black' else ('ew', data[-1][1])
    data.append(('fb', data[-1][1]) if data[-1][0][1] == 'b' else ('fw', data[-1][1]))

    ani = FuncAnimation(fig, update_anim, data, init_func=init_anim)
    writer = AnimatedPNGWriter(fps=1)
    progress_callback = lambda i, n: print(f'Saving frame {i} of {n}')
    ani.save(sys.argv[2], writer=writer, progress_callback=progress_callback)
