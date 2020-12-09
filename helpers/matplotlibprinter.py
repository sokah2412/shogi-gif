import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation
from matplotlib.font_manager import FontProperties
from matplotlib.animation import FuncAnimation
from numpngw import AnimatedPNGWriter
from scipy import ndimage
import numpy as np
import enum
from helpers.board import *
from helpers.printer import *

class MatPlotLibPrinter(Printer):
    def __init__(self, size_factor=1, players=None):
        self.canvas_width = 5 * size_factor
        self.canvas_height = 8.5 * size_factor
        self.players = players

        self.board_width = 8
        self.board_height = 10
        self.board_x = (self.canvas_width - self.board_width) / 2
        self.board_y = (self.canvas_height - self.board_height) / 2
        self.margin = 0.7
        self.column_width = self.board_width / 9
        self.column_height = self.board_height / 9
        #self.zoom = math.sqrt((self.canvas_width * self.canvas_height)/170)
        self.zoom = size_factor

        self.sente_img = plt.imread('resources/shogi-black.png')
        self.gote_img = plt.imread('resources/shogi-white.png')
        self.font = FontProperties(fname='resources/ipamp.ttf', size=14.5*self.zoom)
        self.piece_imgs = self.load_piece_imgs()

        plt.switch_backend('TKAgg') # Needed because QT4Agg yield weird error
        self.fig, self.ax = plt.subplots(figsize=(self.canvas_width, self.canvas_height))
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

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
            self.ax.plot([x, x], [self.board_y, self.board_y + self.board_height], c='black', lw=0.49*self.zoom)
        for y in y_line_coordinates:
            self.ax.plot([self.board_x, self.board_x + self.board_width], [y, y], c='black', lw=0.49*self.zoom)

        # Draw hoshi
        x_hoshi_coordinates = [self.board_x + self.column_width * i for i in [3, 6]]
        y_hoshi_coordinates = [self.board_y + self.column_height * i for i in [3, 6]]
        hoshi_height = 0.15
        hoshi_width = 0.12
        for x in x_hoshi_coordinates:
            for y in y_hoshi_coordinates:
                self.ax.add_patch(Ellipse((x + 0.01, y - 0.01), hoshi_width,
                                          hoshi_height, facecolor='black', fill=True, lw=0.98 * self.zoom))

        # Draw coordinate
        width_shift = self.column_width / 2 - 0.05
        x_nb_coordinates = [self.board_x + self.column_width * i + width_shift for i in range (0, 9)]
        for x, i in zip(x_nb_coordinates, range(9, 0, -1)):
            self.ax.text(x, self.board_y + self.board_height + 0.1, i, fontsize=7.3*self.zoom)

        height_shift = self.column_height / 2 - 0.09
        y_nb_coordinates = [self.board_y + self.column_height * i + height_shift for i in range (0, 9)]
        for y, i in zip(y_nb_coordinates, range(8, -1, -1)):
            self.ax.text(self.board_x + self.board_width + 0.1, y, chr(ord('a') + i), fontsize=7.3*self.zoom)

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
                                    facecolor=white_color, lw=0.98*self.zoom))
        self.ax.add_patch(Rectangle((self.board_x, self.board_y -
                                     self.margin - piece_holder_height), self.board_width,
                                    piece_holder_height, edgecolor='black', fill=True,
                                    facecolor=black_color, lw=0.98*self.zoom))

        # Sente / Gote
        sente = OffsetImage(self.sente_img, zoom=self.zoom*0.49)
        self.ax.add_artist(AnnotationBbox(sente, (self.board_x + 0.8, self.board_y -
                                                  self.margin - 0.47), frameon=False))

        gote = OffsetImage(self.gote_img, zoom=self.zoom*0.49)
        self.ax.add_artist(AnnotationBbox(gote, (self.board_x + self.board_width - 0.8,
                                                 self.board_y + self.board_height +
                                                 self.margin + 0.47),
                                          frameon=False))

        # Players
        if self.players:
            sente, gote = self.players
            self.ax.text(self.board_x, self.board_y - self.margin - piece_holder_height - 0.45,
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
                                    lw=0.48*self.zoom, facecolor=gray_color))

        if move.drop == None: # Piece moved
            x = self.board_x + self.column_width * (8 - move.prev_col)
            y = self.board_y + self.column_height * move.prev_line
            self.ax.add_patch(Rectangle((x, y), self.column_width, self.column_height,
                                        edgecolor='black', fill=True, lw=0.48*self.zoom,
                                        facecolor=gray_color))

    def draw_frame(self, winner=None, move=None):
        if (move):
            self.draw_move(move)
        self.draw_piece_holder(winner)
        self.draw_board()

    def draw_pieces(self, board_pieces, black_hand, white_hand):
        piece_size = 0.8

        for i in range(9):
            for j in range(9):
                p = OffsetImage(self.piece_imgs[board_pieces[i][8 - j]], zoom=self.zoom*0.49)
                x = self.board_x + self.column_width * j + 0.45
                y = self.board_y + self.column_height * i + 0.55
                self.ax.add_artist(AnnotationBbox(p, (x, y), frameon=False))

        for i, (pt, value) in enumerate(black_hand.pieces.items()):
            if value > 0:
                p = Piece(Color.black, pt, False)
                img = OffsetImage(self.piece_imgs[p], zoom=self.zoom*0.455)
                x = self.board_x + piece_size * i + 2.3
                y = self.board_y - self.margin - 1
                self.ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
                self.ax.text(x - 0.1, y - 0.7, value, fontsize=9.7*self.zoom)

        for i, (pt, value) in enumerate(white_hand.pieces.items()):
            if value > 0:
                p = Piece(Color.white, pt, False)
                img = OffsetImage(self.piece_imgs[p], zoom=self.zoom*0.455)
                x = self.board_x + self.board_width - piece_size * i - 2.3
                y = self.board_y + self.board_height + self.margin + 1
                self.ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
                self.ax.text(x - 0.1, y + 0.5, value, fontsize=9.7*self.zoom)


    def save(self, fname, board, data):
        class State(enum.Enum):
            beginning = 0
            playing = 1
            end = 2

        data = [(State.playing, color, move) for color, move in data]
        data.insert(0, (State.beginning, None, None))
        # Print last move with winner color 2 times
        data.append((State.end, data[-1][1], data[-1][2]))
        data.append((State.end, data[-1][1], data[-1][2]))

        self.ax.axis('off')

        def update_anim(data):
            self.ax.clear()
            state, color, move = data
            if state == State.beginning:
                self.draw_frame()
            elif state == State.end:
                self.draw_frame(winner=color, move=move)
            else:
                board.move(color, move)
                self.draw_frame(move=move)
            self.draw_pieces(board.pieces, board.black_hand, board.white_hand)

        ani = FuncAnimation(self.fig, update_anim, data)
        writer = AnimatedPNGWriter(fps=1)
        progress_callback = lambda i, n: print(f'Saving frame {i} of {n}')
        ani.save(fname, writer=writer, progress_callback=progress_callback)
