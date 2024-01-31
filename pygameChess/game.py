import pygame
from controller import Controller


class Game:
    def __init__(self):
        self.running = True
        self.display_surf = None
        self.controller = Controller()

    def render(self):
        pygame.init()
        self.display_surf = pygame.display.set_mode(self.controller.view.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.controller.init_board()
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.controller.select_piece()

                elif event.type == pygame.MOUSEMOTION:
                    self.controller.drag()

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.controller.drop()

            self.display_surf.blit(self.controller.getSurface(), (0, 0))
            pygame.display.update()
        pygame.quit()


if __name__ == '__main__':
    chessGame = Game()
    chessGame.render()
