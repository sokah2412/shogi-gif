import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.font_manager import FontProperties
from scipy import ndimage
import numpy as np
from helpers.board import *

def draw_board(ax, canvas_width, canvas_height, move=None,
               winner=None, players=None):
    # Draw board rectangle

    board_width = 8
    board_height = 10
    board_x = (canvas_width - board_width) / 2
    board_y = (canvas_height - board_height) / 2
    piece_holder_height = board_height / 5
    margin = 0.7

    ax.add_patch(Rectangle((board_x, board_y + board_height + margin),
                           board_width, piece_holder_height,
                           edgecolor='black', fill=False, lw=2))
    ax.add_patch(Rectangle((board_x, board_y), board_width,
                           board_height, edgecolor='black', fill=False, lw=2))
    ax.add_patch(Rectangle((board_x, board_y - margin -
                            piece_holder_height), board_width,
                           piece_holder_height, edgecolor='black',
                           fill=False, lw=2))

    if move != None:
        gray_color = (0.93, 0.93, 0.93)

        # Draw movement indication
        if move.drop == None: # Piece moved
            x = board_x + (board_width / 9) * (8 - move.prev_col)
            y = board_y + (board_height / 9) * move.prev_line
            ax.add_patch(Rectangle((x, y), board_width / 9,
                                   board_height / 9,
                                   edgecolor='black', fill=True, lw=1,
                                   facecolor=gray_color))
        x = board_x + (board_width / 9) * (8 - move.new_col)
        y = board_y + (board_height / 9) * move.new_line
        ax.add_patch(Rectangle((x, y), board_width / 9, board_height /
                               9, edgecolor='black', fill=True, lw=1,
                               facecolor=gray_color))

    # Draw board line
    column_width = board_width / 9
    column_height = board_height / 9
    x_line_coordinates = [board_x + column_width * i for i in range (1, 9)]
    y_line_coordinates = [board_y + column_height * i for i in range (1, 9)]
    for x in x_line_coordinates:
        ax.plot([x, x], [board_y, board_y + board_height], c='black', lw=1)
    for y in y_line_coordinates:
        ax.plot([board_x, board_x + board_width], [y, y], c='black', lw=1)

    # Draw hoshi
    x_hoshi_coordinates = [board_x + column_width * i for i in [3, 6]]
    y_hoshi_coordinates = [board_y + column_height * i for i in [3, 6]]
    hoshi_height = 0.15
    hoshi_width = 0.12
    for x in x_hoshi_coordinates:
        for y in y_hoshi_coordinates:
            ax.add_patch(Ellipse((x + 0.01, y - 0.01), hoshi_width,
                                 hoshi_height, facecolor='black', fill=True, lw=2))

    # Draw coordinate
    width_shift = column_width / 2 - 0.05
    x_nb_coordinates = [board_x + column_width * i + width_shift for i in range (0, 9)]
    for x, i in zip(x_nb_coordinates, range(9, 0, -1)):
        plt.text(x, board_y + board_height + 0.1, i, fontsize=15)

    height_shift = column_height / 2 - 0.09
    y_nb_coordinates = [board_y + column_height * i + height_shift for i in range (0, 9)]
    for y, i in zip(y_nb_coordinates, range(8, -1, -1)):
        plt.text(board_x + board_width + 0.1, y, chr(ord('a') + i), fontsize=15)

    # Draw winner
    if winner != None:
        white_color = 'lightgreen' if winner == 'white' else 'lightcoral'
        black_color = 'lightgreen' if winner == 'black' else 'lightcoral'
        ax.add_patch(Rectangle((board_x, board_y + board_height +
                                margin), board_width,
                               piece_holder_height, edgecolor='black',
                               fill=True, lw=2,
                               facecolor=white_color))
        ax.add_patch(Rectangle((board_x, board_y - margin -
                                piece_holder_height), board_width,
                               piece_holder_height, edgecolor='black',
                               fill=True, lw=2,
                               facecolor=black_color))

    # Sente / Gote
    sente = OffsetImage(plt.imread('resources/shogi-black.png'), zoom=1)
    ax.add_artist(AnnotationBbox(sente, (board_x + 0.8, board_y -
                                         margin - 0.47), frameon=False))

    gote = OffsetImage(plt.imread('resources/shogi-white.png'), zoom=1)
    ax.add_artist(AnnotationBbox(gote, (board_x + board_width - 0.8,
                                        board_y + board_height +
                                        margin + 0.47),
                                 frameon=False))

    # Players
    if players != None:
        font = FontProperties(fname='resources/ipamp.ttf', size=30)
        sente, gote = players
        ax.text(board_x, board_y - margin - piece_holder_height - 0.4,
                sente, fontproperties=font)
        if (gote[0] >= 'a' and gote[0] <= 'z') or (gote[0] >= 'A' and gote[0] <= 'Z'):
            size_letter = 0.2
        else:
            size_letter = 0.33
        size_gote = len(gote) * size_letter
        ax.text(board_x + board_width - size_gote, board_y +
                board_height + margin + piece_holder_height + 0.15,
                gote, fontproperties=font)

    return board_width, board_height, board_x, board_y, margin

def draw_pieces(ax, pieces, piece_imgs, board_info):
    board_width, board_height, board_x, board_y, margin = board_info
    piece_size = 0.8

    for i in range(9):
        for j in range(9):
            p = OffsetImage(piece_imgs[pieces.get(i, 8 - j)], zoom=1)
            x = board_x + (board_width / 9) * j + 0.45
            y = board_y + (board_height / 9) * i + 0.55
            ax.add_artist(AnnotationBbox(p, (x, y), frameon=False))

    for i, (pt, value) in enumerate(pieces.black_hand.pieces.items()):
        if value > 0:
            p = Piece(Color.black, pt, False)
            img = OffsetImage(piece_imgs[p], zoom=0.93)
            x = board_x + piece_size * i + 2.3
            y = board_y - margin - 1
            ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
            plt.text(x - 0.1, y - 0.7, value, fontsize=20)

    for i, (pt, value) in enumerate(pieces.white_hand.pieces.items()):
        if value > 0:
            p = Piece(Color.white, pt, False)
            img = OffsetImage(piece_imgs[p], zoom=0.93)
            x = board_x + board_width - piece_size * i - 2.3
            y = board_y + board_height + margin + 1
            ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
            plt.text(x - 0.1, y + 0.5, value, fontsize=20)

def load_piece_imgs():
    PATH = 'resources/pieces/'
    pieces_str = ['knight', 'lance', 'king', 'gold', 'bishop', 'pawn',
                  'silver', 'rook', 'pknight', 'plance', 'pbishop', 'ppawn',
                  'psilver', 'prook']
    pieces = {Piece(None, PieceType.void, None) : np.zeros((0, 0))}
    for piece_str in pieces_str:
        piece_img = (plt.imread(PATH + piece_str + '_letter.png') * 255).astype('uint8')

        promoted = piece_str[0] == 'p' and piece_str[1] != 'a'
        piece_type = PieceType[piece_str[promoted:]]
        pieces[Piece(Color.black, piece_type, promoted)] = piece_img
        pieces[Piece(Color.white, piece_type, promoted)] = ndimage.rotate(piece_img, 180)
    return pieces
