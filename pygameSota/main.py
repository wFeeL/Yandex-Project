import math
import pygame
import os
import random

tile_grid_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tile_sprites = pygame.sprite.Group()
mouse = pygame.sprite.Group()
ultra_sprites = pygame.sprite.Group()


def load_image(name):
    image = pygame.image.load(os.path.join(name))
    return image


def make_ultra_tiles():
    j = 0
    for i in ultra_tiles_ready_play:
        if not i[0]:
            tile = stencils_tiles_ready_play[-1]
            i[0] = Ultra_tile(tile[:-3], [colors[j]], tile[-3:-1], tile[-1], i[1], 0, new_score[i[2]])
        j += 1


def make_tiles():
    for i in tiles_ready_play:
        if not i[0]:
            tile = random.choice(stencils_tiles_ready_play)  # stencils_tiles_ready_play[1]
            i[0] = Tile(tile[:-3], random.sample(colors, len(tile[:-3])), tile[-3:-1], tile[-1], i[1])


def spawn(shema, color, coor_grid, tile, kill):
    global color_family_score
    a = 0
    ss = []
    for _ in color:
        try:
            e = tile_grid['.'.join(str(x) for x in coor_grid) if type(coor_grid) == list else coor_grid]
            ss.append('.'.join(str(x) for x in coor_grid) if type(coor_grid) == list else coor_grid)
            s = [int(h) for h in
                 ('.'.join(str(x) for x in coor_grid) if type(coor_grid) == list else coor_grid).split('.')]
            for j in range(len(shema[a])):
                s[j] += shema[a][j]
            coor_grid = s[:]
            a += 1 if a < len(shema) - 1 else 0
        except KeyError:
            ''
    e = 0
    if len(ss) == len(color):
        for i in ss:
            if tile_grid[i].get_score():
                e += 1
        if not e:
            red_score = ultra_tiles_ready_play[0][0].get_score()
            green_score = ultra_tiles_ready_play[1][0].get_score()
            blue_score = ultra_tiles_ready_play[2][0].get_score()
            for i in range(len(ss)):
                tile_grid[ss[i]].new_color(color[i], kill, 1)
            color_family_score = {'red': 1, 'blue': 0, 'green': 0}
            new_red_score = red_score - ultra_tiles_ready_play[0][0].get_score()
            new_green_score = green_score - ultra_tiles_ready_play[1][0].get_score()
            new_blue_score = blue_score - ultra_tiles_ready_play[2][0].get_score()
            if new_red_score or new_green_score or new_blue_score:
                if new_red_score and new_green_score and new_blue_score:
                    ultra_tiles_ready_play[0][0].new_score(-new_red_score * 2)
                    ultra_tiles_ready_play[1][0].new_score(-new_green_score * 2)
                    ultra_tiles_ready_play[2][0].new_score(-new_blue_score * 2)
                elif new_red_score and new_green_score:
                    ultra_tiles_ready_play[0][0].new_score(-new_red_score)
                    ultra_tiles_ready_play[1][0].new_score(-new_green_score)
                elif new_red_score and new_blue_score:
                    ultra_tiles_ready_play[0][0].new_score(-new_red_score)
                    ultra_tiles_ready_play[2][0].new_score(-new_blue_score)
                elif new_blue_score and new_green_score:
                    ultra_tiles_ready_play[2][0].new_score(-new_blue_score)
                    ultra_tiles_ready_play[1][0].new_score(-new_green_score)
            if kill:
                tiles_ready_play[tile][0].kill()
                tiles_ready_play[tile][0] = 0
            else:
                ultra_tiles_ready_play[tile][0].kill()
                ultra_tiles_ready_play[tile][0] = 0
                ultra_tiles_ready_play[tile][2] += 1


class Tile(pygame.sprite.Sprite):
    def __init__(self, neighbour, colorss, razmer, shema, xy):
        super().__init__(all_sprites, tile_sprites)
        self.x0, self.y0 = xy[0], xy[1]
        self.x, self.y = self.x0, self.y0
        self.shema = shema
        self.neighbour = neighbour
        self.colors = colorss
        self.image = self.colors[0]
        self.rect = pygame.Rect(self.x, self.y, razmer[0], razmer[1])
        self.center = [self.neighbour[0][0] + 76, self.neighbour[0][1] + 66]
        self.center_yes = 0
        self.score = 1

    def update(self):
        for i in range(len(self.neighbour)):
            screen.blit(self.colors[i], (self.x + self.neighbour[i][0] - self.center[0] * self.center_yes,
                                         self.y + self.neighbour[i][1] - self.center[1] * self.center_yes))

    def get_pos(self):
        return self.x, self.y

    def get_rect(self):
        return self.rect

    def new_pos(self, x, y, center=0):
        self.x = x
        self.y = y
        self.center_yes = center

    def get_center(self):
        return self.center

    def null(self):
        self.x, self.y = self.x0, self.y0
        self.center_yes = 0

    def spawn(self):
        return self.shema, self.colors

    def smeshenie(self):
        self.colors = self.colors[1:] + self.colors[:1] if len(self.colors) != 1 else self.colors

    def get_score(self):
        return self.score


class Ultra_tile(Tile):
    def __init__(self, neighbour, colorss, razmer, shema, xy, ready_for_play, score):
        super().__init__(neighbour, colorss, razmer, shema, xy)
        self.ready_for_play = ready_for_play
        self.score = score
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', 60)
        ultra_sprites.add(self)
        self.new_score()

    def update(self):
        screen.blit(self.colors[0], (self.x + self.neighbour[0][0] - self.center[0] * self.center_yes,
                                     self.y + self.neighbour[0][1] - self.center[1] * self.center_yes))
        screen.blit(self.text, (self.x + 25 - self.center[0] * self.center_yes,
                                self.y + 33 - self.center[1] * self.center_yes))

    def new_score(self, new_scose=0):
        self.score += new_scose
        self.score = 0 if int(self.score) < 0 else self.score
        self.text = self.font.render(str(self.score), False, (0, 0, 0))

    def get_score(self):
        return self.score


class Tile_from_the_grid(pygame.sprite.Sprite):
    def __init__(self, coor, image, coor_grid, score=0):
        super().__init__(all_sprites, tile_grid_sprites)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.score = score
        self.coor = coor
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = coor[1]
        self.rect.y = coor[0]
        self.color = 0
        self.coor_grid = coor_grid
        self.center = [self.coor[0] + 76, self.coor[1] + 62]
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', 60)
        self.text = self.font.render(str(self.score), False, (0, 0, 0))

    def update(self, coor=0):
        screen.blit(self.image, (self.coor[0], self.coor[1] + (self.coor[1] // 61) * 4))
        screen.blit(self.text, (self.coor[0] + 25,
                                self.coor[1] + 33)) if self.score else ''

    def collide(self):
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]

        sqx = (x - self.center[0]) ** 2
        sqy = (y - self.center[1]) ** 2

        if math.sqrt(sqx + sqy) < 68:
            return self.coor_grid
        return 0

    def null(self):
        self.image = load_image('pygameSota/resources/tile3.png')
        self.score = 0

    def new_color(self, image, ultra, score=1):
        self.image = image
        self.score = score
        self.text = self.font.render(str(self.score) if self.score > 1 else '', False, (0, 0, 0))
        self.color = colors_for_proverka[colors.index(image)]
        color_family[colors_for_proverka[colors.index(image)]].append([self.coor_grid])
        l = 0
        for i in proverka:
            s = [int(h) for h in self.coor_grid.split('.')]
            for j in range(len(i)):
                s[j] += i[j]
            coor_grid_proverka = '.'.join(str(k) for k in s)
            if coor_grid_proverka in tile_grid.keys() and tile_grid[coor_grid_proverka].get_score() \
                    and tile_grid[coor_grid_proverka].get_color() == self.color:
                for h in color_family[self.color][:]:
                    if coor_grid_proverka in h and self.coor_grid not in h:
                        color_family[self.color][-1] += h
                        color_family[self.color].remove(h)
                        l += 1
                        continue
        for h in color_family[self.color][-1]:
            color_family_score[self.color] += tile_grid[h].get_score()
        ultra_tiles_ready_play[colors.index(image)][0].new_score(
            -color_family_score[self.color] + (1 if self.color == 'red' else 0)) if l else ''
        if not ultra:
            for i in color_family[self.color][-1]:
                if i != self.coor_grid:
                    tile_grid[i].null()
            self.score = color_family_score[self.color]
            self.score = self.score - 1 if self.color == 'red' else self.score
            self.text = self.font.render(str(self.score), False, (0, 0, 0))
            color_family[self.color][-1] = [color_family[self.color][-1][0]]

    def get_score(self):
        return self.score

    def get_color(self):
        return self.color if self.color else 0


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Перетаскивание')
    size = width, height = 1650, 950
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 255))
    tile_grid = {

        '3.0.-3': [319, 1],

        '3.-1.-2': [213, 62], '2.1.-3': [424, 62],

        '3.-2.-1': [107, 123], '2.0.-2': [319, 123], '1.2.-3': [531, 123],

        '3.-3.0': [1, 184], '2.-1.-1': [213, 184], '1.1.-2': [424, 184], '0.3.-3': [636, 184],

        '2.-2.0': [107, 245], '1.0.-1': [319, 245], '0.2.-2': [531, 245],

        '2.-3.1': [1, 306], '1.-1.0': [213, 306], '0.1.-1': [424, 306], '-1.3.-2': [636, 306],

        '1.-2.1': [107, 367], '0.0.0': [319, 367], '-1.2.-1': [531, 367],

        '1.-3.2': [1, 428], '0.-1.1': [213, 428], '-1.1.0': [424, 428], '-2.3.-1': [636, 428],

        '0.-2.2': [107, 489], '-1.0.1': [319, 489], '-2.2.0': [531, 489],

        '0.-3.3': [1, 550], '-1.-1.2': [213, 550], '-2.1.1': [424, 550], '-3.3.0': [636, 550],

        '-1.-2.-3': [107, 611], '-2.0.2': [319, 611], '-3.2.1': [531, 611],

        '-2.-1.3': [213, 672], '-3.1.2': [424, 672],

        '-3.0.3': [319, 733]
    }  # y.x.z
    proverka = [[1, 0, -1], [0, 1, -1], [-1, 1, 0], [-1, 0, 1], [0, -1, 1], [1, -1, 0]]
    color_family = {'red': [], 'blue': [], 'green': []}
    color_family_score = {'red': 1, 'blue': 0, 'green': 0}

    stencils_tiles_ready_play = [[[1, 1], [1, 123], [1, 245], 213, 550, [[-1, 0, 1], [-1, 0, 1]]],
                                 [[1, 1], [107, 62], [213, 123], 424, 248, [[-1, 1, 0], [-1, 1, 0]]],
                                 [[213, 1], [107, 62], [1, 123], 424, 428, [[0, -1, 1], [0, -1, +1]]],

                                 [[1, 1], [1, 123], [107, 62], 319, 428, [[-1, 0, 1], [0, 1, -1]]],
                                 [[107, 1], [107, 123], [1, 62], 319, 245, [[-1, 0, 1], [1, -1, 0]]],

                                 [[1, 1], [1, 123], 213, 245, [[-1, 0, 1]]],
                                 [[1, 1], [107, 62], 319, 184, [[-1, 1, 0]]],
                                 [[107, 1], [1, 62], 319, 184, [[0, -1, 1]]],
                                 [[1, 1], 213, 123, [[0, 0, 0]]]]

    r = 1
    colors = [load_image('pygameSota/resources/tile3_red.png'), load_image('pygameSota/resources/tile3_green.png'),
              load_image('pygameSota/resources/tile3_blue.png')]
    colors_for_proverka = ['red', 'green', 'blue']
    new_score = [10, 25, 50, 100, 150, 200, 300, 500, 750, 1000]
    ultra_tiles_ready_play = [[0, (1230, 10), 0], [0, (1347, 82), 0], [0, (1463, 154), 0]]
    tiles_ready_play = [[0, (860, 10)], [0, (860, 570)], [0, (1230, 570)]]
    move = 0
    move_tile = ''
    surf_move = pygame.Surface((0, 0))
    rectangle = pygame.Rect(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                            pygame.mouse.get_pos()[0] + 1, pygame.mouse.get_pos()[1] + 1)
    for i in tile_grid:
        tile_grid[i] = Tile_from_the_grid(tile_grid[i], 'pygameSota/resources/tile3.png', i)
        tile_grid[i].update()
    while r:
        screen.fill((255, 255, 255))
        tile_grid_sprites.update()
        list_ivent = pygame.event.get()

        for event in list_ivent:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in tiles_ready_play:
                    a = i[0].get_rect()
                    if a.collidepoint(event.pos):
                        move = 1
                        move_tile = i
                for i in ultra_tiles_ready_play:
                    if not int(i[0].get_score()):
                        a = i[0].get_rect()
                        if a.collidepoint(event.pos):
                            move = 1
                            move_tile = i
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                for i in tiles_ready_play:
                    a = i[0].get_rect()
                    if a.collidepoint(event.pos):
                        i[0].smeshenie()
            if move and event.type == pygame.MOUSEMOTION:
                screen.blit(surf_move, (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
                x, y = move_tile[0].get_pos()
                move_tile[0].new_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 1)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and move:
                for i in tile_grid:
                    if tile_grid[i].collide():
                        spawn(move_tile[0].spawn()[0], move_tile[0].spawn()[1], i,
                              (tiles_ready_play if move_tile in tiles_ready_play else ultra_tiles_ready_play).index(
                                  move_tile),
                              1 if move_tile in tiles_ready_play else 0)
                        break

                move = 0
                screen.blit(surf_move, (0, 0))
                move_tile[0].null() if move_tile[0] else ''
                move_tile = ''
                mouse.draw(screen)

        make_tiles()
        make_ultra_tiles()
        tile_sprites.update()
        ultra_sprites.update()
        pygame.display.update()
