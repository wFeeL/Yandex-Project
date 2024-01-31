import pygame


class MoveableImage:
    def __init__(self, path, pos, size):
        self.path = path
        self.pos = pos
        self.currentPos = self.x, self.y = pos
        self.size = self.width, self.height = size

        image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(image, size)

        self.pulled = False

    def drop(self):
        assert self.pulled is True
        self.pulled = False

    def update_fields(self, new_pos):
        self.currentPos = new_pos
        self.x, self.y = new_pos[0], new_pos[1]

    def move_image(self, new_pos):
        self.pos = new_pos
        assert self.currentPos == self.pos

    def is_clicked(self, coords):
        x, y = coords[0], coords[1]
        image_x, image_y = self.pos[0], self.pos[1]

        x_result = image_x <= x <= image_x + self.width
        y_result = image_y <= y <= image_y + self.height
        return x_result and y_result

    def is_pulled(self, coords):
        assert self.pulled is False
        self.pulled = self.is_clicked(coords)
        return self.pulled
