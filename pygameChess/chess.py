import copy
from pieces import Piece, Colour, Pawn, Rook, Knight, Bishop, Queen, King


class Chess:
    def __init__(self):
        self.turn_colour = Colour.white  # Intnum class
        self.board = []
        self.is_over = False

    def create_board(self):
        for y in range(8):
            row = [None] * 8
            if y == 0:
                row = set_pieces(y, Colour.black)
            elif y == 1:
                row = set_pawns(y, Colour.black)
            elif y == 6:
                row = set_pawns(y, Colour.white)
            elif y == 7:
                row = set_pieces(y, Colour.white)
            self.board.append(row)

    def move(self, start, end):
        x1, y1 = start
        x2, y2 = end
        start_pos = self.board[y1][x1]
        white_in_check, black_in_check = self.calculate_checks(self.board)

        if start_pos is None or start_pos.colour != self.turn_colour:
            return False

        if start_pos.colour == Colour.white:
            in_check = white_in_check
        else:
            in_check = black_in_check

        candidates = start_pos.get_squares_id(self.board, in_check)

        move_correct = end in candidates

        copyBoard = copy.deepcopy(self.board)
        copyFromPiece = copyBoard[y1][x1]
        copyBoard[y1][x1] = None
        copyBoard[y2][x2] = copyFromPiece
        copyFromPiece.move_piece(end)
        white_in_check, black_in_check = self.calculate_checks(copyBoard)

        if (copyFromPiece.colour == -1 and white_in_check) or (copyFromPiece == 1 and black_in_check):
            return False

        if self.turn_colour == Colour.white:
            in_check = white_in_check
        else:
            in_check = black_in_check

        move_correct = move_correct and not in_check

        if move_correct:
            self.board[y1][x1] = None
            self.board[y2][x2] = start_pos
            start_pos.move_piece(end)
            self.turn_colour *= -1  # Change turn
        return move_correct

    def calculate_checks(self, board):
        white_in_check, black_in_check = False, False
        white_king, black_king = 0, 0

        for row in board:
            for piece in row:
                if isinstance(piece, King) and piece.colour == Colour.white:
                    white_king = piece
                if isinstance(piece, King) and piece.colour == Colour.black:
                    black_king = piece
        for row in board:
            for piece in row:
                if piece is not None and piece.colour == Colour.white:
                    if type(black_king) != int:
                        if black_king.position in piece.get_squares_id(self.board, False):
                            black_in_check = True
                elif piece is not None and piece.colour == Colour.black:
                    if type(white_king) != int:
                        if white_king.position in piece.get_squares_id(self.board, False):
                            white_in_check = True
        return white_in_check, black_in_check


def set_pawns(y, colour):
    return [Pawn((x, y), colour) for x in range(8)]


def set_pieces(y, colour):
    constructPieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
    return [constructPieces[x]((x, y), colour) for x in range(8)]
