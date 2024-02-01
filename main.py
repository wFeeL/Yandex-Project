import pygame
import pygame_menu
import subprocess

pygame.init()
surface = pygame.display.set_mode((600, 400))


def start_the_chess():
    try:
        subprocess.run('pygameChess/dist/game.exe', check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing game.exe: {e}")


def start_the_sota():
    try:
        subprocess.run('pygameSota/dist/main.exe', check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing game.exe: {e}")


menu = pygame_menu.Menu('Welcome', 400, 300,
                        theme=pygame_menu.themes.THEME_SOLARIZED)
menu.add.button('Chess', start_the_chess)
menu.add.button('Sota', start_the_sota)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(surface)
