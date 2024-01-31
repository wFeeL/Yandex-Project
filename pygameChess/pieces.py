from enum import IntEnum
from itertools import chain, product


class Colour(IntEnum):
    white = -1
    black = 1


class Piece:
    def __init__(self, coords, colour):
        self.position = self.x, self.y = coords
        self.colour = colour

    def get_squares_id(self, board, in_check):
        pass

    def get_path(self, x1, y1):
        pass

    def is_grid(self, coords):
        return 0 <= coords[0] <= 7 and 0 <= coords[1] <= 7

    def get_board(self, candidate, board):
        assert (self.is_grid(candidate))
        return board[candidate[1]][candidate[0]]

    def move_piece(self, coords):
        self.position = coords
        self.x = coords[0]
        self.y = coords[1]

    def is_free(self, candidate, board):
        if self.is_grid(candidate):
            return board[candidate[1]][candidate[0]] is None
        else:
            return False

    def is_ableToCapture(self, candidate, board):
        return (self.is_grid(candidate) and self.get_board(candidate, board) is not None and
                self.get_board(candidate, board).colour != self.colour)


class Pawn(Piece):
    def __init__(self, coords, colour):
        super().__init__(coords, colour)
        self.isMoved = False

    def get_squares_id(self, board, in_check):
        direction = self.colour
        candidates = []

        move_forward = (self.x, self.y + direction)
        move_forward_first = (self.x, self.y + 2 * direction)
        [move_leftD, move_rightD] = [(self.x - 1, self.y + direction), (self.x + 1, self.y + direction)]

        if self.is_free(move_forward, board):
            candidates.append(move_forward)

        if self.is_ableToCapture(move_leftD, board):
            candidates.append(move_leftD)

        if self.is_ableToCapture(move_rightD, board):
            candidates.append(move_rightD)

        if not self.isMoved and self.is_free(move_forward_first, board) and self.is_free(move_forward, board):
            candidates.append(move_forward_first)
        return candidates

    def get_attack_squares(self):
        direction = self.colour
        return [(self.x - 1, self.y + direction), (self.x + 1, self.y + direction)]

    def get_path(self, x1, y1):
        direction = self.colour
        path = []
        if x1[0] == y1[0]:
            path += [(x1[0], x1[1] + direction)]
        if y1[1] == x1[1] + 2:
            path += [(x1[0], x1[1] + 2 * direction)]
        return path

    def move_piece(self, coords):
        super().move_piece(coords)
        self.isMoved = True


class Knight(Piece):
    def get_moves(self):
        moves = product([1, -1], [2, -2])  # using itertools to get correct moves
        return list(chain.from_iterable([[(self.x + x, self.y + y), (self.x + y, self.y + x)] for (x, y) in moves]))

    def get_squares_id(self, board, in_check):
        candidates = self.get_moves()
        move_legal = list(
            filter(lambda candidate: self.is_free(candidate, board) or self.is_ableToCapture(candidate, board),
                   candidates))
        return move_legal

    def get_path(self, x1, y1):
        pass


class Bishop(Piece):
    def get_moves(self):
        moves = [1, -1]
        result = [(self.x + scale * x, self.y + scale * y) for (x, y) in product(moves, repeat=2)
                  for scale in range(1, 8)]

        if self.position in result:
            result.remove(self.position)

        return result

    def get_squares_id(self, board, in_check):
        candidates = self.get_moves()
        move_legal = list(
            filter(lambda candidate: self.is_free(candidate, board) or self.is_ableToCapture(candidate, board),
                   candidates))
        move_correct = list(
            filter(lambda xy2: all(board[y][x] is None for (x, y) in self.get_path(self.position, xy2)), move_legal))
        return move_correct

    def get_path(self, start, end):
        (x1, y1) = start
        (x2, y2) = end
        assert abs(x1 - x2) == abs(y1 - y2)
        path_len = abs(x1 - x2)
        if x2 > x1:
            if y2 > y1:
                path = [(x1 + i, y1 + i) for i in range(1, path_len)]
            else:
                path = [(x1 + i, y1 - i) for i in range(1, path_len)]
        else:
            if y2 > y1:
                path = [(x1 - i, y1 + i) for i in range(1, path_len)]
            else:
                path = [(x1 - i, y1 - i) for i in range(1, path_len)]
        return path


class Rook(Piece):
    def get_moves(self):
        move_horizontal = [(self.x, y) for y in range(1, 9)]
        move_vertical = [(x, self.y) for x in range(1, 9)]

        result = move_vertical + move_horizontal

        if self.position in result:
            result.remove(self.position)
        return result

    def get_squares_id(self, board, in_check):
        condition = self.get_moves()

        move_legal = list(
            filter(lambda candidate: self.is_free(candidate, board) or self.is_ableToCapture(candidate, board),
                   condition))
        move_correct = list(
            filter(lambda xy2: all(self.is_free(candidate, board)
                                   for candidate in self.get_path(self.position, xy2)), move_legal))
        return move_correct

    def get_path(self, start, end):
        x1, y1 = start
        x2, y2 = end
        assert x1 == x2 or y1 == y2

        if x1 == x2:
            if y2 > y1:
                path = [(x1, y1 + i) for i in range(1, y2 - y1)]
            else:
                path = [(x1, y1 - i) for i in range(1, y1 - y2)]
        else:
            if x2 > x1:
                path = [(x1 + i, y1) for i in range(1, x2 - x1)]
            else:
                path = [(x1 - i, y1) for i in range(1, x1 - x2)]
        return path


class Queen(Piece):
    def get_moves(self):
        bishop_moves = Bishop(self.position, self.colour).get_moves()
        rook_moves = Rook(self.position, self.colour).get_moves()
        result = bishop_moves + rook_moves

        if self.position in result:
            result.remove(self.position)
        return result

    def get_squares_id(self, board, in_check):
        move_bishop = Bishop(self.position, self.colour).get_squares_id(board, in_check)
        move_rook = Rook(self.position, self.colour).get_squares_id(board, in_check)
        return move_bishop + move_rook

    def get_path(self, start, end):
        bishop = Bishop(self.position, self.colour)
        rook = Rook(self.position, self.colour)
        if start[0] == end[0] or start[1] == end[1]:
            return rook.get_path(start, end)
        else:
            return bishop.get_path(start, end)


class King(Piece):
    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.isCheck = False

    def get_squares_id(self, board, in_check):
        moves = [(self.x + x, self.y + y) for (x, y) in product([-1, 0, 1], repeat=2)]
        moves.remove(self.position)
        move_legal = set(
            filter(lambda candidate: self.is_free(candidate, board) or self.is_ableToCapture(candidate, board),
                   moves))
        squares_attacked = set()
        for row in board:
            for piece in row:
                if piece is not None and piece.colour != self.colour and not isinstance(piece, King):
                    if isinstance(piece, Pawn):
                        squares_attacked.update(piece.get_attack_squares())
                    else:
                        new_list = piece.get_moves()
                        squares_attacked.update(new_list)

        move_correct = list(filter(lambda candidate: not (candidate in squares_attacked), move_legal))
        return move_correct

    def get_attack_squares(self):
        moves = [(self.x + x, self.y + y) for (x, y) in product([-1, 0, 1], repeat=2)]
        moves.remove(self.position)
        return moves

    def get_path(self, start, end):
        return []

    def set_check(self):
        self.isCheck = True

    def set_check_off(self):
        self.isCheck = False
