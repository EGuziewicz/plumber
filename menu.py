from enum import Enum

import pygame

from settings import Settings
from util import blit_text, WHITE


class IterEnum(Enum):
    def _get_offset(self, offset):
        members = list(self.__class__)
        index = members.index(self)
        return members[(index + offset) % len(members)]

    def next(self):
        return self._get_offset(1)

    def prev(self):
        return self._get_offset(-1)

    def custom_str(self, *args, **kwargs):
        return str(self.value)


class Menu:
    MENU_BACKGROUND_COLOR = (255, 255, 255)
    SELECTED_BACKGROUND_COLOR = (100, 100, 100, 100)

    class Option(Enum):
        def next(self):
            pass

        def prev(self):
            pass

    def __init__(self, main=None, screen=None, settings=None):
        self.main = main
        self.screen = screen
        self.opt = list(self.Option)[0]
        self.settings = settings

    def handle_key(self, key):
        if key == pygame.K_DOWN:
            self.opt = self.opt.next()
        elif key == pygame.K_UP:
            self.opt = self.opt.prev()
        elif key == pygame.K_RETURN:
            self.handle_return()
        elif key == pygame.K_ESCAPE:
            self.handle_esc()

    def handle_return(self):
        pass

    def handle_esc(self):
        pass

    def blitme(self):
        self.screen.fill(self.MENU_BACKGROUND_COLOR)
        options_num = len(list(self.Option))

        for i, option in enumerate(self.Option):
            bg_color = self.SELECTED_BACKGROUND_COLOR if self.opt is option else WHITE
            height = (self.settings.screen_height() / (2 * options_num)) * (i + 2)
            blit_text(option.custom_str(self.settings), (self.settings.screen_width_center(), height), self.screen, 60, bg_color=bg_color)


class MainMenu(Menu):
    class Option(IterEnum):
        NEW_GAME = 'NEW GAME'
        SETTINGS = 'SETTINGS'
        QUIT = 'QUIT'

    def handle_return(self):
        if self.opt is self.Option.NEW_GAME:
            self.main.set_game_mode()
        elif self.opt is self.Option.SETTINGS:
            self.main.set_settings_mode()
        else:  # self.opt is self.Option.QUIT
            self.main.set_quitting_mode()


class SettingsMenu(Menu):
    class Option(IterEnum):
        SOUND = 'SOUND'
        DIFFICULTY = 'DIFFICULTY'
        BACK = 'BACK'

        def custom_str(self, settings, *args, **kwargs):
            if self is self.SOUND:
                return f'{self.value}: {"ON" if settings.sound else "OFF"}'
            elif self is self.DIFFICULTY:
                return f'{self.value}: {settings.difficulty + 1}'
            else:   # self is self.BACK
                return self.value

    def handle_return(self):
        if self.opt is self.Option.SOUND:
            self.settings.sound = self.settings.sound ^ True
        elif self.opt is self.Option.DIFFICULTY:
            self.settings.difficulty = (self.settings.difficulty + 1) % Settings.MAX_DIFFICULTY
        else:   # self.opt is self.Option.BACK
            self.main.set_menu_mode()

    def handle_esc(self):
        self.main.set_menu_mode()


class GameMenu(Menu):
    class Option(IterEnum):
        RESTART = 'RESTART'
        BACK_TO_MENU = 'BACK TO MENU'
        BACK = 'BACK'

    def __init__(self, game=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game

    def handle_return(self):
        if self.opt is self.Option.RESTART:
            self.main.set_game_mode()
        elif self.opt is self.Option.BACK_TO_MENU:
            self.main.set_menu_mode()
        else:   # self.opt is self.Option.BACK
            self.game.menu = None

    def handle_esc(self):
        self.game.menu = None
