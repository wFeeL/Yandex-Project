import pygame
from view import View
from chess import Chess


class Controller:
    def __init__(self):
        self.chess = Chess()
        self.view = View()

    def init_board(self):
        self.chess.create_board()
        self.view.init_view()

    def select_piece(self):
        coordinates = pygame.mouse.get_pos()
        self.view.set_piece(coordinates)

    def drop(self):
        if self.view.dragging is not None:
            first_coords = pygame.mouse.get_pos()
            second_coords = self.view.dragging.pos

            toCo = view_coords(first_coords, self.view.dragging.size)
            fromCo = view_coords(second_coords, self.view.dragging.size)

            if self.chess.move(tuple_to_int(fromCo), tuple_to_int(toCo)):
                self.view.remove_image(first_coords)
                self.view.drop(first_coords)
            else:
                self.view.drop(self.view.dragging.pos)
            self.view.dragging = None

    def drag(self):
        if self.view.dragging is not None:
            coordinates = pygame.mouse.get_pos()
            self.view.take_piece(coordinates)

    def getSurface(self):
        return self.view.display_surface


def tuple_to_int(t):
    return int(t[0]), int(t[1])


def view_coords(pos, size):
    return tuple(map(lambda a, b: a // b, pos, size))
