import pygame
from MoveableImage import MoveableImage


class View:
    def __init__(self):
        self.running = True
        self.background = None
        self.dragging = None

        self.size = self.width, self.height = 800, 800
        self.piece_size = self.piece_width, self.piece_height = 100, 100
        self._display_surf = pygame.Surface(self.size)

        self.mImages = []

    def init_view(self):
        board = pygame.image.load('pygameChess/resources/board.jpg').convert()
        board = pygame.transform.scale(board, self.size)

        self.background = board

        colours = ['w', 'b']
        path_of_pieces = ['r', 'n', 'b', 'q', 'k']
        board_row = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']

        for colour in colours:
            y = 0 if colour == 'b' else self.height - self.piece_height
            for piece in path_of_pieces:
                for i, pieceName in enumerate(board_row):
                    if pieceName == piece:
                        x = i * self.piece_width
                        pI = MoveableImage(f'pygameChess/resources/{colour}{piece}.png', (x, y), self.piece_size)
                        self.mImages.append(pI)
            y = self.piece_height if colour == 'b' else self.height - 2 * self.piece_height

            for x in range(0, self.width, self.piece_width):
                pI = MoveableImage(f'pygameChess/resources/{colour}p.png', (x, y), self.piece_size)
                self.mImages.append(pI)
        self.update()

    def set_piece(self, mouse_pos):
        image = self.get_piece(mouse_pos)

        if image is not None:
            image.is_pulled(mouse_pos)
            self.dragging = image
            return

        self.dragging = None

    def get_piece(self, mouse_pos):
        for image in self.mImages:
            if image.is_clicked(mouse_pos):
                return image

    def take_piece(self, coords):
        assert self.dragging is not None
        coords = tuple(map(lambda a, b: a - b / 2, coords, self.dragging.size))
        self.dragging.update_fields(coords)
        self.update()

    def drop(self, coords):
        x, y = coords
        x = (x // self.piece_height) * self.piece_width
        y = (y // self.piece_width) * self.piece_height

        self.dragging.update_fields((x, y))
        self.dragging.move_image((x, y))
        self.dragging.drop()
        self.dragging = None
        self.update()

    def remove_image(self, coords):
        piece = self.get_piece(coords)
        if piece in self.mImages:
            self.mImages.remove(piece)

    def update(self):
        self._display_surf.blit(self.background, (0, 0))

        for movingI in self.mImages:
            self._display_surf.blit(movingI.image, movingI.currentPos)

        if self.dragging is not None:
            self._display_surf.blit(self.dragging.image, self.dragging.currentPos)

    def get_surface(self):
        return self._display_surf

    @property
    def display_surface(self):
        return self._display_surf
