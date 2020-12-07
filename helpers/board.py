import enum

class PieceType(enum.Enum):
    pawn = 'P'
    lance = 'L'
    knight = 'N'
    silver = 'S'
    gold = 'G'
    bishop = 'B'
    rook = 'R'
    king = 'K'
    void = 'V'

    def __str__(self):
        return str(self.value)

class Color(enum.Enum):
    black = False
    white = True

class Piece:
    def __init__(self, color, piece_type, promoted):
        self.color = color
        self.piece_type = piece_type
        self.promoted = promoted

    def __str__(self):
        return f'color: {self.color}, type: {self.piece_type}, promoted: {self.promoted}'
    def __hash__(self):
        if self.piece_type == PieceType.void:
            return hash((None, PieceType.void, None))
        else:
            return hash((self.color, self.piece_type, self.promoted))

    def __eq__(self, other):
        if self.piece_type == PieceType.void:
            return self.piece_type == other.piece_type
        else:
            return (self.color, self.piece_type, self.promoted) == (other.color, other.piece_type, other.promoted)

    def __ne__(self, other):
        return not(self == other)

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
        self.prev_col = -1
        self.prev_line = -1
        self.new_col = int(move_str[2]) - 1
        self.new_line = 8 - (ord(move_str[3]) - ord('a'))
        self.promoted = move_str[-1] == '+'

        if move_str[1] == '*':
            self.drop = PieceType(move_str[0])
        else:
            # Adapt move_str format to board format
            self.prev_col = int(move_str[0]) - 1
            self.prev_line = 8 - (ord(move_str[1]) - ord('a'))

class Board:
    def __init__(self, black_board, white_board):
        self.pieces = self.init_board(black_board, white_board)
        self.white_hand = Hand()
        self.black_hand = Hand()

    def init_board(self, black_board, white_board):
        pieces = [[Piece(None, PieceType.void, None)] * 9 for i in range(9)]

        for i, row_str in enumerate(black_board):
            for j, col_str in enumerate(row_str[::-1]):
                pieces[i][j] = Piece(Color.black, PieceType(col_str), False)

        for i, row_str in enumerate(white_board[::-1]):
            for j, col_str in enumerate(row_str):
                pieces[6 + i][j] = Piece(Color.white, PieceType(col_str), False)

        return pieces

    def get(self, x, y):
        return self.pieces[x][y]

    def move(self, color, move):
        if move.drop != None:
            drop_piece = Piece(color, move.drop, False)
            self.pieces[move.new_line][move.new_col] = drop_piece
            if color == Color.white:
                self.white_hand.remove_piece(drop_piece.piece_type)
            else:
                self.black_hand.remove_piece(drop_piece.piece_type)
        else:
            piece = self.pieces[move.prev_line][move.prev_col]
            self.pieces[move.prev_line][move.prev_col] = Piece(None, PieceType.void, None)

            piece_opp = self.pieces[move.new_line][move.new_col]
            piece.promoted = piece.promoted or move.promoted
            self.pieces[move.new_line][move.new_col] = piece

            if piece_opp.piece_type != PieceType.void:
                if color == Color.white:
                    self.white_hand.add_piece(piece_opp.piece_type)
                else:
                    self.black_hand.add_piece(piece_opp.piece_type)
