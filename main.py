from enum import Enum
from time import sleep

import pygame

from game import Game
from menu import MainMenu, SettingsMenu
from settings import Settings
from util import blit_text, WHITE


class Plumber:
    GAME_NAME = 'Plumber'
    FPS = 60

    class Mode(Enum):
        MENU = 0
        SETTINGS = 1
        GAME = 2
        QUITTING = 3

    def __init__(self):
        self.game = None
        self.menu = None
        self.mode = None
        self.settings = Settings()

        pygame.init()
        pygame.display.set_caption(self.GAME_NAME)
        self.display = pygame.display.set_mode(self.settings.screen_size())

    def set_menu_mode(self):
        self.mode = self.Mode.MENU
        self.menu = MainMenu(main=self, screen=self.display, settings=self.settings)

    def set_game_mode(self):
        self.mode = self.Mode.GAME
        self.game = Game(main=self, screen=self.display, settings=self.settings)

    def set_settings_mode(self):
        self.mode = self.Mode.SETTINGS
        self.menu = SettingsMenu(main=self, screen=self.display, settings=self.settings)

    def set_quitting_mode(self):
        self.mode = self.Mode.QUITTING

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.set_quitting_mode()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.mode is self.Mode.GAME:
                    self.game.handle_click(pos)
            if event.type == pygame.KEYDOWN:
                if self.mode in {self.Mode.MENU, self.Mode.SETTINGS}:
                    self.menu.handle_key(event.key)
                elif self.mode is self.Mode.GAME:
                    self.game.handle_key(event.key)

    def run_loop(self):
        if self.mode is self.Mode.GAME:
            self.game.run_loop()

    def render_quitting(self):
        self.display.fill(WHITE)
        blit_text('Thanks for playing!', self.settings.screen_center(), self.display, 60)

    def render(self):
        self.display = pygame.display.set_mode(self.settings.screen_size())

        if self.mode in {self.Mode.MENU, self.Mode.SETTINGS}:
            self.menu.blitme()
        elif self.mode == self.Mode.GAME:
            self.game.blitme()
        else:   # self.mode == self.Mode.QUITTING
            self.render_quitting()

        pygame.display.update()

    def run(self):
        self.set_menu_mode()

        while self.mode is not self.Mode.QUITTING:
            self.process_events()
            self.run_loop()
            self.render()
            sleep(1 / self.FPS)

        sleep(0.5)
        pygame.quit()


if __name__ == '__main__':
    plumber = Plumber()
    plumber.run()
