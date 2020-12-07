import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import enum
import sys
import shogi.KIF
from numpngw import AnimatedPNGWriter
from helpers.printer import *
from helpers.board import *

class State(enum.Enum):
    beginning = 0
    playing = 1
    end = 2

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
    ax.axis('off')

    board = Board(board_str, board_str)
    printer = Printer(ax, board, canvas_width, canvas_height, players)

    def update_anim(data):
        ax.clear()
        state, color, move = data
        if state == State.beginning:
            printer.draw_frame()
        elif state == State.end:
            printer.draw_frame(winner=color, move=move)
        else:
            board.move(color, move)
            printer.draw_frame(move=move)
        printer.draw_pieces()

    data = [(State.playing, Color(i % 2), Move(move)) for i, move in enumerate(kif['moves'])]
    data.insert(0, (State.beginning, None, None))
    data.append((State.end, data[-1][1], data[-1][2])) # Print last move with winner color

    ani = FuncAnimation(fig, update_anim, data)
    writer = AnimatedPNGWriter(fps=1)
    progress_callback = lambda i, n: print(f'Saving frame {i} of {n}')
    ani.save(sys.argv[2], writer=writer, progress_callback=progress_callback)
