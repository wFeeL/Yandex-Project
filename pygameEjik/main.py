import os
import sys
import random
import sqlite3
import pygame

from pygame.locals import *

from PyQt5.QtGui import QIcon

pygame.init()
pygame.mixer.pre_init()

size = width, height = 700, 700
tile_width = tile_height = 70

pygame.display.set_caption("Ежик!!!")
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)

clock = pygame.time.Clock()
FPS = 50
GRAVITY = 1

MYEVENTTYPE = pygame.USEREVENT + 1
pygame.time.set_timer(MYEVENTTYPE, 2000)

# счётчик яблок с учётом пропущенных
count = 0
# итоговый результат игрока
apple_count = 0

# звук стука яблока, если его поймали
apple_music = pygame.mixer.Sound("pygameEjik/data/stuk.wav")

# создаём группы спрайтов, с которыми удобно
# проверять столкновения
all_sprites = pygame.sprite.Group()
ejik_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
palki_group = pygame.sprite.Group()
lestniza_group = pygame.sprite.Group()
up_lestnizi = pygame.sprite.Group()
down_lestnizi = pygame.sprite.Group()
group_tibloki = pygame.sprite.Group()

# названия картинок лежат в списках для удобства
images = ['ejik.png', 'ejik_2.png']
vidi_palok = ['palka_vl.png', 'palka_nl.png', 'palka_vr.png', 'palka_nr.png']


def load_image(name, colorkey=None):
    fullname = os.path.join('pygameEjik/data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "pygameEjik/data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# вспомогательная функция для ввода никнейма
def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass


# вспомогательная функция для ввода никнейма
def display_box(screen, message):
    fontobject = pygame.font.Font(None, 18)
    pygame.draw.rect(screen, (0, 0, 0),
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 10,
                      200, 20), 0)
    pygame.draw.rect(screen, (255, 255, 255),
                     ((screen.get_width() / 2) - 102,
                      (screen.get_height() / 2) - 12,
                      204, 24), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                    ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


# функция для ввода никнейма
def ask(screen, question):
    pygame.font.init()
    current_string = []
    display_box(screen, question + ": " + "".join(current_string))
    while 1:
        inkey = get_key()
        if inkey == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == K_RETURN:
            break
        elif inkey == K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ": " + "".join(current_string))
    return "".join(current_string)


# функция для создания яблок справа и слева,
# передаём нужные картинку и положение
def proverka_apples(x, y):
    if (x == 0 and y == 1) or (x == 0 and y == 4):
        image = load_image("apple_left.png")
        per = 'left'
    elif (x == 9 and y == 1) or (x == 9 and y == 4):
        image = load_image("apple_right.png")
        per = 'right'
    return image, per


# эта функция выводит на экран количество яблок
# с учётом пропущенных
def count_tibloki(count):
    intro_text = [f"      Очки(не для глаз): {count}"]
    font = pygame.font.Font(None, 30)
    string_render = font.render(intro_text[0], True, pygame.Color('black'))
    intro_rect = string_render.get_rect()
    intro_rect.x = 210
    screen.blit(string_render, intro_rect)


# функция закрытия и выхода из игры
def terminate():
    pygame.quit()
    sys.exit()


# функция стартового экрана
def start_screen():
    # запускаем стартовую музыку
    pygame.mixer.music.load("pygameEjik/data/st_end_music.wav")
    pygame.mixer.music.play(-1, 0.0, 20000)

    intro_text = ['"Ежик!!!"', "",
                  "Правила игры",
                  "1 - Перемещайте ежика при помощи стрелочек,",
                  "собирая при этом яблоки. За них начисляются очки.",
                  "2 - Передвигаться вверх и вниз можно только по лестницам.",
                  "3 - По небу ходить запрещено!",
                  "4 - Со временем скорость увеличивается.",
                  "5 - Старайтесь не пропускать яблоки, иначе, если",
                  "счётчик станет ниже нуля, вы проиграете.",
                  "6 - Яблоко можно собрать только в том случае, если",
                  "вы перехватите его до начала падения. Если попытаетесь",
                  "после, то у вас ничего не выйдет.",
                  "7 - Лучшие результаты игроков записываются.",
                  "8 - Пожалуйста, не пытайтесь сломать игру!",
                  ]

    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    # выводим текст на экран
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


# функция конечного экрана
# принимает на вход никнейм игрока
def end_screen(inp):
    # выключаем фоновую музыку
    pygame.mixer.music.stop()
    # запускаем конечную музыку
    pygame.mixer.music.load("pygameEjik/data/st_end_music.wav")
    pygame.mixer.music.play(-1, 0.0, 20000)

    # соединяемся с базой данных
    connection = sqlite3.connect("pygameEjik/data/Ejik_DataBase.sqlite")
    cur = connection.cursor()
    # вносим изменения в базу данных
    cur.execute("""INSERT INTO records(user, ochki) VALUES (?, ?)""", (inp, apple_count))
    connection.commit()
    # возвращаем из базы данных никнеймы и количество собранных
    # яблок трёх лучших игроков
    spis = cur.execute("""SELECT user, ochki FROM records
                          ORDER BY ochki DESC""").fetchmany(3)

    intro_text = ["Поздравляю!",
                  "Ваш ежик усталь:)", "",
                  "Сколько же вы собрали яблок?",
                  f"А вот столько: {apple_count}", "",
                  "Это отличный результат!",
                  "Продолжайте в том же духе и устанавливайте новые рекорды;)", ""
                  ]

    if len(spis) == 3:
        intro_text += ["Вот лучшие игроки:",
                       f"{spis[0][0]}, {spis[0][1]}",
                       f"{spis[1][0]}, {spis[1][1]}",
                       f"{spis[2][0]}, {spis[2][1]}"
                       ]
    else:
        intro_text += ['К сожалению, эту игру запустило только небольшое',
                       'количество игроков, поэтому нельзя составить "топ 3".']

    fon = pygame.transform.scale(load_image('fon_end.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    # выводим текст на экран
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


# словарь объектов фона для каждой клетки поля
tile_images = {
    'sky': load_image('sky.jpeg'),
    'sky_obl': load_image('sky_obl.png'),
    'grass': load_image('grass.png'),
    'grass_zv': load_image('grass_zv.png'),
    'korzinka': load_image('korzinka.png'),
    'derevo': load_image('derevo.png'),
}
# изначально загружаем картинку ежика,
# который смотрит налево
ejik_image = load_image(images[0])


# ежик
class AnimatedEjik(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(ejik_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    # режем картинку на кадры
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # обновление смены кадров
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    # метод проверяет столкновение с разными частями лестниц
    # и возвращает их условные названия
    def bam(self):
        if pygame.sprite.spritecollideany(self, lestniza_group):
            return 'obich'
        if pygame.sprite.spritecollideany(self, up_lestnizi):
            return 'up'
        if pygame.sprite.spritecollideany(self, down_lestnizi):
            return 'down'

    # метод, отвечающий за движение ежика по стрелочкам
    def update_go(self, events, cop, x, y):
        if events[pygame.K_UP] and not cop[pygame.K_UP]:
            # если ежик не находится на верхней лестнице,
            # но стоит на любой другой,
            # то мы ему не запрещаем двигаться наверх
            if self.bam() and self.bam() != 'up':
                self.rect.y -= 70
        elif events[pygame.K_RIGHT] and not cop[pygame.K_RIGHT]:
            self.frames = []
            # при движении направо мы меняем картинку ежика
            # на соответствующую, делая "поворот"
            self.cut_sheet(load_image(images[1]), 4, 2)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(x, y)
            # этой проверкой даём возможность двигаться направо,
            # если ежик стоит на нижней лестнице или на земле
            if self.bam() != 'obich' and self.bam() != 'up':
                self.rect.x += 70
        elif events[pygame.K_DOWN] and not cop[pygame.K_DOWN]:
            # если ежик не находится на нижней лестнице,
            # но стоит на любой другой,
            # то мы ему не запрещаем двигаться вниз
            if self.bam() and self.bam() != 'down':
                self.rect.y += 70
        elif events[pygame.K_LEFT] and not cop[pygame.K_LEFT]:
            self.frames = []
            # при движении налево мы меняем картинку ежика
            # на соответствующую, делая "поворот"
            self.cut_sheet(load_image(images[0]), 4, 2)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(x, y)
            # этой проверкой даём возможность двигаться налево,
            # если ежик стоит на нижней лестнице или на земле
            if self.bam() != 'obich' and self.bam() != 'up':
                self.rect.x -= 70


# тыблоко
class Tibloko(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, pos):
        super().__init__(all_sprites, group_tibloki)
        global count
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.flag = False
        # задаём правильное направление скорости
        if pos == 'left':
            self.vx = 2
        elif pos == 'right':
            self.vx = -2
        self.vy = 1
        # увеличиваем скорость
        if 5 <= apple_count < 10:
            self.vx *= 2
            self.vy *= 2
        if 10 <= apple_count < 20:
            self.vx *= 2
            self.vy *= 2
        if apple_count >= 20:
            self.vx *= 2
            self.vy *= 2
        self.rect.x, self.rect.y = x * tile_width, y * tile_height

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    # режем картинку на кадры
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # яблоки катятся
    def update(self):
        global count
        global apple_count
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.vx, self.vy)

        # падение (если ежик не поймал яблоко)
        if not pygame.sprite.spritecollideany(self, palki_group):
            self.flag = True
            self.vy += self.gravity
            self.rect.y += self.vy
        # если ежик поймал яблоко
        if pygame.sprite.spritecollideany(self, ejik_group) and not self.flag:
            apple_music.play()
            count += 1
            apple_count += 1
            print(count)
            self.kill()

        # уничтожаем яблоки, вылетевшие за рамки экрана
        if not self.rect.colliderect(screen_rect):
            count -= 1
            self.kill()


# клетка поля
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


# палки
class Palka(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, palki_group)
        # выбираем вид палки
        if (x == 1 and y == 2) or (x == 1 and y == 5):
            image = load_image(vidi_palok[0])
        elif (x == 2 and y == 2) or (x == 2 and y == 5):
            image = load_image(vidi_palok[1])
        elif (x == 8 and y == 2) or (x == 8 and y == 5):
            image = load_image(vidi_palok[2])
        elif (x == 7 and y == 2) or (x == 7 and y == 5):
            image = load_image(vidi_palok[3])
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height


# лестницы
class Lestniza(pygame.sprite.Sprite):
    image = load_image("lestniza.png")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        # выбираем вид лестницы
        if (x == 3 and y == 3) or (x == 6 and y == 3):
            self.add(up_lestnizi)
        elif (x == 3 and y == 7) or (x == 6 and y == 7):
            self.add(down_lestnizi)
        else:
            self.add(lestniza_group)
        self.image = Lestniza.image
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_width
        self.rect.y = y * tile_height


# функция, создающая уровень
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('sky', x, y)
            elif level[y][x] == ')':
                Tile('sky_obl', x, y)
            elif level[y][x] == '*':
                Tile('sky', x, y)
                Tile('derevo', x, y)
                Tile('korzinka', x, y)
            elif level[y][x] == '#':
                Tile('grass', x, y)
            elif level[y][x] == '(':
                Tile('grass_zv', x, y)
            elif level[y][x] == '$':
                Tile('sky', x, y)
                Lestniza(x, y)
            elif level[y][x] == '%':
                Tile('grass', x, y)
                Lestniza(x, y)
            elif level[y][x] == '"':
                Tile('sky', x, y)
                Palka(x, y)
            elif level[y][x] == '@':
                Tile('grass', x, y)
                # создаём ежика
                new_player = AnimatedEjik(load_image(images[0]), 4, 2, x * 70, y * 70)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


start_screen()

# выключаем стартовую музыку
pygame.mixer.music.stop()
# включаем фоновую музыку
pygame.mixer.music.load("pygameEjik/data/fon_music.wav")
pygame.mixer.music.play(-1, 0.0, 20000)

player, level_x, level_y = generate_level(load_level('level_1.txt'))
events = pygame.key.get_pressed()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == MYEVENTTYPE:
            # список с возможными начальными позициями яблок
            spis = [(0, 1), (0, 4), (9, 1), (9, 4)]
            # выбираем рандомное положение яблока
            x, y = random.choice(spis)
            # используем функцию, чтобы получить нужное изображение
            # по координатам
            image, pos = proverka_apples(x, y)
            # создаём яблоко
            Tibloko(image, 4, 2, x, y, pos)
    if count < 0:
        # вызываем окно для ввода никнейма
        inp = ask(screen, 'Как вас зовут?')
        end_screen(inp)

    screen.fill((0, 0, 0))
    all_sprites.update()
    ejik_group.update()

    cop = events
    events = pygame.key.get_pressed()

    player.update_go(events, cop, player.rect.x, player.rect.y)
    group_tibloki.update()

    all_sprites.draw(screen)
    ejik_group.draw(screen)

    count_tibloki(count)
    clock.tick(10)
    pygame.display.flip()
pygame.quit()
