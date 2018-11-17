from pathlib import Path
from random import choice

import pygame

from menu import GameMenu
from pipe import Pipe
from util import blit_text


class Game:
    TOP_TEXT_FONT_SIZE = 25
    BOTTOM_TEXT_FONT_SIZE = 50
    SRC_TILE_COLOR = (153, 248, 255, 90)
    GOOD_TEXT_COLOR = (35, 211, 50)
    BAD_TEXT_COLOR = (234, 95, 44)
    WIN_TEXT = 'CONGRATS! PRESS "ESC" FOR MORE OPTIONS.'
    LOSE_TEXT = 'UPS! CLICK ANYWHERE TO TRY AGAIN.'
    START_FLOW_BTN_TEXT = 'START FLOW'
    WATER_SPRITE_PATH = str(Path('assets', 'water.png'))

    def __init__(self, main=None, screen=None, settings=None):
        self.main = main
        self.screen = screen
        self.settings = settings
        self.bottom_text_rect = None
        self.reset_on_next_click = False
        self.top_text = ''
        self.top_text_color = None
        self.menu = None
        self.flow_path = []
        self.board = self.generate_good_board()

    def is_in_board(self, x, y):
        return 0 <= x < self.settings.x_pipes_num() and 0 <= y < self.settings.y_pipes_num()

    def generate_good_board(self):
        start = (-1, 0)
        finish = (self.settings.x_pipes_num(), self.settings.y_pipes_num() - 1)

        # Find a sequence of tiles (disregarding their kinds) leading from start to finish via repeated random walk.
        while True:
            path = [start]

            while True:
                choices = ((0, 1), (1, 0), (-1, 0), (0, -1))
                valid_choices = []
                for c in choices:
                    try_x, try_y = path[-1][0] + c[0], path[-1][1] + c[1]
                    if (try_x, try_y) not in path and (self.is_in_board(try_x, try_y) or (try_x, try_y) == finish):
                        valid_choices.append(c)
                if not valid_choices:
                    break

                x_off, y_off = choice(valid_choices)
                x, y = path[-1]
                next_x, next_y = x + x_off, y + y_off
                path.append((next_x, next_y))
                if (next_x, next_y) == finish:
                    break

            if path[-1] == finish:
                break

        # Find the correct kinds of tiles on the found sequence so that it can be walked from start to finish.
        # The rest of the tiles have random kinds.
        kinds = [[None for _ in range(self.settings.x_pipes_num())] for _ in range(self.settings.y_pipes_num())]

        for (x1, y1), (x2, y2), (x3, y3) in zip(path[:-2], path[1:-1], path[2:]):
            prev_x_diff, prev_y_diff = x2 - x1, y2 - y1
            x_diff, y_diff = x3 - x2, y3 - y2

            if x_diff == 0 and prev_x_diff == 0 or y_diff == 0 and prev_y_diff == 0:
                kinds[y2][x2] = Pipe.Kind.STRAIGHT
            else:
                kinds[y2][x2] = Pipe.Kind.BEND

        # Create the board.
        return [
            [
                Pipe(
                    screen=self.screen, settings=self.settings, kind=kinds[j][i],
                    x=(self.settings.SCREEN_PIPE_PADDING + i) * Pipe.SPRITE_LENGTH,
                    y=(self.settings.SCREEN_PIPE_PADDING + j) * Pipe.SPRITE_LENGTH,
                ) for i in range(self.settings.x_pipes_num())
            ] for j in range(self.settings.y_pipes_num())
        ]

    def start_flow(self):
        self.flow_path = []
        pipe = Pipe(kind=Pipe.Kind.STRAIGHT, direction=Pipe.Direction.RIGHT)
        entry_dir = Pipe.Direction.LEFT
        x, y = -1, 0
        while True:
            pipe, entry_dir, x, y = pipe.get_connected(self.board, x, y, entry_dir)
            self.flow_path.append((pipe, (x, y)))
            if pipe is None:
                break

    def finish_flow(self, last_x, last_y):
        if last_x == len(self.board[0]) and last_y == len(self.board) - 1:
            self.top_text_color = self.GOOD_TEXT_COLOR
            self.top_text = self.WIN_TEXT
        else:
            self.top_text_color = self.BAD_TEXT_COLOR
            self.top_text = self.LOSE_TEXT

        self.reset_on_next_click = True

    def reset_fullness(self):
        for row in self.board:
            for pipe in row:
                pipe.full = False

        self.top_text = None
        self.top_text_color = None

    def blitme(self):
        if self.menu:
            self.menu.blitme()
            return

        white = (255, 255, 255)
        self.screen.fill(white)

        for row in self.board:
            for pipe in row:
                pipe.blitme()

        bottom_text_center = (self.settings.screen_width_center(), self.board[-1][0].y + 1.5 * Pipe.SPRITE_LENGTH)
        bottom_text_bg_color = (
            GameMenu.SELECTED_BACKGROUND_COLOR
            if self.bottom_text_rect and self.bottom_text_rect.collidepoint(pygame.mouse.get_pos())
            else GameMenu.MENU_BACKGROUND_COLOR
        )
        self.bottom_text_rect = blit_text(
            self.START_FLOW_BTN_TEXT, bottom_text_center, self.screen,
            size=self.BOTTOM_TEXT_FONT_SIZE, bg_color=bottom_text_bg_color
        )

        if self.top_text:
            top_text_center = (self.settings.screen_width_center(), self.board[0][0].y - 0.5 * Pipe.SPRITE_LENGTH)
            blit_text(
                self.top_text, top_text_center, self.screen, size=self.TOP_TEXT_FONT_SIZE, color=self.top_text_color
            )

        water_src_pos = (
            (self.settings.SCREEN_PIPE_PADDING - 1) * Pipe.SPRITE_LENGTH,
            self.settings.SCREEN_PIPE_PADDING * Pipe.SPRITE_LENGTH
        )
        water_dst_pos = (
            (self.settings.SCREEN_PIPE_PADDING + self.settings.x_pipes_num()) * Pipe.SPRITE_LENGTH,
            (self.settings.SCREEN_PIPE_PADDING + self.settings.y_pipes_num() - 1) * Pipe.SPRITE_LENGTH,
        )
        water_image = pygame.image.load(self.WATER_SPRITE_PATH)
        water_image.convert_alpha()
        background = water_image.copy()
        background.fill(self.SRC_TILE_COLOR)
        self.screen.blit(background, water_src_pos)
        self.screen.blit(background, water_dst_pos)
        self.screen.blit(water_image, water_src_pos)
        self.screen.blit(water_image, water_dst_pos)

    def handle_click(self, pos):
        if self.flow_path or self.menu is not None:
            return

        if self.reset_on_next_click:
            self.reset_fullness()
            self.reset_on_next_click = False

        for row in self.board:
            for pipe in row:
                if pipe.x < pos[0] < pipe.x + Pipe.SPRITE_LENGTH and pipe.y < pos[1] < pipe.y + Pipe.SPRITE_LENGTH:
                    pipe.handle_click()

        if self.bottom_text_rect.collidepoint(pos):
            self.start_flow()

    def handle_key(self, key):
        if self.flow_path:
            return

        if self.menu is not None:
            self.menu.handle_key(key)
            return

        if key == pygame.K_ESCAPE and not self.menu:
            self.menu = GameMenu(game=self, main=self.main, screen=self.screen, settings=self.settings)
            return

        if self.reset_on_next_click:
            self.reset_fullness()
            self.reset_on_next_click = False

        if key == pygame.K_RETURN:
            self.start_flow()

    def run_loop(self):
        if not self.flow_path:
            return

        pipe, (x, y) = self.flow_path[0]
        self.flow_path = self.flow_path[1:]
        if not self.flow_path:
            self.finish_flow(x, y)
        else:
            pipe.full = True
