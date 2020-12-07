import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.font_manager import FontProperties
from scipy import ndimage
import numpy as np
from helpers.board import *

class Printer():
    def __init__(self, ax, board, canvas_width, canvas_height, players=None):
        self.ax = ax
        self.board = board
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.players = players

        self.board_width = 8
        self.board_height = 10
        self.board_x = (self.canvas_width - self.board_width) / 2
        self.board_y = (self.canvas_height - self.board_height) / 2
        self.margin = 0.7
        self.column_width = self.board_width / 9
        self.column_height = self.board_height / 9

        self.sente_img = plt.imread('resources/shogi-black.png')
        self.gote_img = plt.imread('resources/shogi-white.png')
        self.font = FontProperties(fname='resources/ipamp.ttf', size=30)
        self.piece_imgs = self.load_piece_imgs()

    def load_piece_imgs(self):
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

    def draw_board(self):
        self.ax.add_patch(Rectangle((self.board_x, self.board_y),
                                    self.board_width, self.board_height,
                                    edgecolor='black', fill=False, lw=2))

        # Draw board line
        x_line_coordinates = [self.board_x + self.column_width * i for i in range (1, 9)]
        y_line_coordinates = [self.board_y + self.column_height * i for i in range (1, 9)]
        for x in x_line_coordinates:
            self.ax.plot([x, x], [self.board_y, self.board_y + self.board_height], c='black', lw=1)
        for y in y_line_coordinates:
            self.ax.plot([self.board_x, self.board_x + self.board_width], [y, y], c='black', lw=1)

        # Draw hoshi
        x_hoshi_coordinates = [self.board_x + self.column_width * i for i in [3, 6]]
        y_hoshi_coordinates = [self.board_y + self.column_height * i for i in [3, 6]]
        hoshi_height = 0.15
        hoshi_width = 0.12
        for x in x_hoshi_coordinates:
            for y in y_hoshi_coordinates:
                self.ax.add_patch(Ellipse((x + 0.01, y - 0.01), hoshi_width,
                                    hoshi_height, facecolor='black', fill=True, lw=2))

        # Draw coordinate
        width_shift = self.column_width / 2 - 0.05
        x_nb_coordinates = [self.board_x + self.column_width * i + width_shift for i in range (0, 9)]
        for x, i in zip(x_nb_coordinates, range(9, 0, -1)):
            self.ax.text(x, self.board_y + self.board_height + 0.1, i, fontsize=15)

        height_shift = self.column_height / 2 - 0.09
        y_nb_coordinates = [self.board_y + self.column_height * i + height_shift for i in range (0, 9)]
        for y, i in zip(y_nb_coordinates, range(8, -1, -1)):
            self.ax.text(self.board_x + self.board_width + 0.1, y, chr(ord('a') + i), fontsize=15)

    def draw_piece_holder(self, winner=None):
        piece_holder_height = self.board_height / 5
        white_color = 'white'
        black_color = 'white'

        if winner:
            white_color = 'lightgreen' if winner == Color.white else 'lightcoral'
            black_color = 'lightgreen' if winner == Color.black else 'lightcoral'

        self.ax.add_patch(Rectangle((self.board_x, self.board_y +
                                     self.board_height + self.margin), self.board_width,
                                    piece_holder_height, edgecolor='black', fill=True,
                                    facecolor=white_color, lw=2))
        self.ax.add_patch(Rectangle((self.board_x, self.board_y -
                                     self.margin - piece_holder_height), self.board_width,
                                    piece_holder_height, edgecolor='black', fill=True,
                                    facecolor=black_color, lw=2))

        # Sente / Gote
        sente = OffsetImage(self.sente_img, zoom=1)
        self.ax.add_artist(AnnotationBbox(sente, (self.board_x + 0.8, self.board_y -
                                                  self.margin - 0.47), frameon=False))

        gote = OffsetImage(self.gote_img, zoom=1)
        self.ax.add_artist(AnnotationBbox(gote, (self.board_x + self.board_width - 0.8,
                                                 self.board_y + self.board_height +
                                                 self.margin + 0.47),
                                          frameon=False))

        # Players
        if self.players:
            sente, gote = self.players
            self.ax.text(self.board_x, self.board_y - self.margin - piece_holder_height - 0.4,
                         sente, fontproperties=self.font)
            if (gote[0] >= 'a' and gote[0] <= 'z') or (gote[0] >= 'A' and gote[0] <= 'Z'):
                size_letter = 0.2
            else:
                size_letter = 0.33
            size_gote = len(gote) * size_letter
            self.ax.text(self.board_x + self.board_width - size_gote,
                         self.board_y + self.board_height +
                         self.margin + piece_holder_height + 0.15,
                         gote, fontproperties=self.font)

    def draw_move(self, move):
        gray_color = (0.93, 0.93, 0.93)

        x = self.board_x + self.column_width * (8 - move.new_col)
        y = self.board_y + self.column_height * move.new_line
        self.ax.add_patch(Rectangle((x, y), self.column_width,
                                    self.column_height,
                                    edgecolor='black', fill=True,
                                    lw=1, facecolor=gray_color))

        if move.drop == None: # Piece moved
            x = self.board_x + self.column_width * (8 - move.prev_col)
            y = self.board_y + self.column_height * move.prev_line
            self.ax.add_patch(Rectangle((x, y), self.column_width, self.column_height,
                                        edgecolor='black', fill=True, lw=1,
                                        facecolor=gray_color))

    def draw_frame(self, winner=None, move=None):
        if (move):
            self.draw_move(move)
        self.draw_piece_holder(winner)
        self.draw_board()

    def draw_pieces(self):
        piece_size = 0.8

        for i in range(9):
            for j in range(9):
                p = OffsetImage(self.piece_imgs[self.board.get(i, 8 - j)], zoom=1)
                x = self.board_x + self.column_width * j + 0.45
                y = self.board_y + self.column_height * i + 0.55
                self.ax.add_artist(AnnotationBbox(p, (x, y), frameon=False))

        for i, (pt, value) in enumerate(self.board.black_hand.pieces.items()):
            if value > 0:
                p = Piece(Color.black, pt, False)
                img = OffsetImage(self.piece_imgs[p], zoom=0.93)
                x = self.board_x + piece_size * i + 2.3
                y = self.board_y - self.margin - 1
                self.ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
                self.ax.text(x - 0.1, y - 0.7, value, fontsize=20)

        for i, (pt, value) in enumerate(self.board.white_hand.pieces.items()):
            if value > 0:
                p = Piece(Color.white, pt, False)
                img = OffsetImage(self.piece_imgs[p], zoom=0.93)
                x = self.board_x + self.board_width - piece_size * i - 2.3
                y = self.board_y + self.board_height + self.margin + 1
                self.ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
                self.ax.text(x - 0.1, y + 0.5, value, fontsize=20)
