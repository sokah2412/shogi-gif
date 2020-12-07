import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.font_manager import FontProperties
from scipy import ndimage
import numpy as np
import enum
import sys
import shogi.KIF
from numpngw import AnimatedPNGWriter

class PieceType(enum.Enum):
    pawn = 'P'
    lance = 'L'
    knight = 'N'
    silver = 'S'
    gold = 'G'
    bishop = 'B'
    rook = 'R'
    king = 'K'

class Color(enum.Enum):
    black = False
    white = True

class Piece:
    def __init__(self, color, piece_type, promoted):
        self.color = color
        self.piece_type = piece_type
        self.promoted = promoted

class Hand:
    def __init__(self):
        self.pieces = {member : 0 for _, member in PieceType.__members__.items()}
        del(self.pieces[PieceType.king])

    def add_piece(self, piece_type):
        self.pieces[piece_type] += 1

    def remove_piece(self, piece_type):
        self.pieces[piece_type] -= 1

class Move:
    def __init__(self, move_str):
        self.drop = None
        if move_str[1] == '*':
            self.drop = PieceType(move_str[0])
        else:
            # Adapt move_str format to board format
            self.prev_col = int(move_str[0]) - 1
            self.prev_line = 8 - (ord(move_str[1]) - ord('a'))
        self.new_col = int(move_str[2]) - 1
        self.new_line = 8 - (ord(move_str[3]) - ord('a'))
        self.promoted = move_str[-1] == '+'

class Board_pieces:
    def __init__(self):
        self.pieces = [[Piece.void] * 9 for i in range(9)]
        self.white_hand = Hand()
        self.black_hand = Hand()
        self.init_board()

    def init_board(self):
        self.pieces[2] = [Piece.black_pawn] * 9
        self.pieces[0][0] = Piece.black_lance
        self.pieces[0][8] = Piece.black_lance
        self.pieces[0][1] = Piece.black_knight
        self.pieces[0][7] = Piece.black_knight
        self.pieces[0][2] = Piece.black_silver
        self.pieces[0][6] = Piece.black_silver
        self.pieces[0][3] = Piece.black_gold
        self.pieces[0][5] = Piece.black_gold
        self.pieces[0][4] = Piece.black_king
        self.pieces[1][1] = Piece.black_rook
        self.pieces[1][7] = Piece.black_bishop

        self.pieces[6] = [Piece.white_pawn] * 9
        self.pieces[8][0] = Piece.white_lance
        self.pieces[8][8] = Piece.white_lance
        self.pieces[8][1] = Piece.white_knight
        self.pieces[8][7] = Piece.white_knight
        self.pieces[8][2] = Piece.white_silver
        self.pieces[8][6] = Piece.white_silver
        self.pieces[8][3] = Piece.white_gold
        self.pieces[8][5] = Piece.white_gold
        self.pieces[8][4] = Piece.white_king
        self.pieces[7][7] = Piece.white_rook
        self.pieces[7][1] = Piece.white_bishop

    def get(self, x, y):
        return self.pieces[x][y]

    def move(self, color, move):
        if move.drop != None:
            drop_piece = Piece((color, move.drop, False))
            self.pieces[move.new_line][move.new_col] = drop_piece
            if color == Color.white:
                self.white_hand.remove_piece(drop_piece.type)
            else:
                self.black_hand.remove_piece(drop_piece.type)

        else:
            piece = self.pieces[move.prev_line][move.prev_col]
            self.pieces[move.prev_line][move.prev_col] = Piece.void

            piece_opp = self.pieces[move.new_line][move.new_col]
            self.pieces[move.new_line][move.new_col] = Piece((color, piece.type, move.promoted))

            if piece_opp != Piece.void:
                if color == Color.white:
                    self.white_hand.add_piece(piece_opp.type)
                else:
                    self.black_hand.add_piece(piece_opp.type)

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
            p = Piece((Color.black, pt, False))
            img = OffsetImage(piece_imgs[p], zoom=0.93)
            x = board_x + piece_size * i + 2.3
            y = board_y - margin - 1
            ax.add_artist(AnnotationBbox(img, (x, y), frameon=False))
            plt.text(x - 0.1, y - 0.7, value, fontsize=20)

    for i, (pt, value) in enumerate(pieces.white_hand.pieces.items()):
        if value > 0:
            p = Piece((Color.white, pt, False))
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
    pieces = {Piece.void : np.zeros((0, 0))}
    for piece_str in pieces_str:
        piece_img = (plt.imread(PATH + piece_str + '_letter.png') * 255).astype('uint8')

        promoted = piece_str[0] == 'p' and piece_str[1] != 'a'
        piece_type = PieceType[piece_str[promoted:]]
        pieces[Piece((Color.black, piece_type, promoted))] = piece_img
        pieces[Piece((Color.white, piece_type, promoted))] = ndimage.rotate(piece_img, 180)
    return pieces

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f'usage: python {sys.argv[0]} kifu_name gif_name')
        exit()

    plt.switch_backend('TKAgg') # Needed because QT4Agg yield weird error

    canvas_width = 10
    canvas_height = 17

    fig, ax = plt.subplots(figsize=(canvas_width, canvas_height))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    pieces = Board_pieces()
    piece_imgs = load_piece_imgs()
    kif = shogi.KIF.Parser.parse_file(sys.argv[1])[0]
    players = kif['names'][shogi.BLACK], kif['names'][shogi.WHITE]

    def init_anim():
        ax.axis('off')
        board_info = draw_board(ax, canvas_width, canvas_height)
        draw_pieces(ax, pieces, piece_imgs, board_info)

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
            pieces.move(color, move)
        board_info = draw_board(ax, canvas_width, canvas_height,
                                winner=winner, move=move,
                                players=players)
        draw_pieces(ax, pieces, piece_imgs, board_info)

    data = [('black', move) if i % 2 == 0 else ('white', move) for i,
            move in enumerate(kif['moves'])]
    data.insert(0, ('bi',''))
    data[-1] = ('eb', data[-1][1]) if data[-1][0] == 'black' else ('ew', data[-1][1])
    data.append(('fb', data[-1][1]) if data[-1][0][1] == 'b' else ('fw', data[-1][1]))

    ani = FuncAnimation(fig, update_anim, data, init_func=init_anim)
    writer = AnimatedPNGWriter(fps=1)
    progress_callback = lambda i, n: print(f'Saving frame {i} of {n}')
    ani.save(sys.argv[2], writer=writer, progress_callback=progress_callback)
