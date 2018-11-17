from enum import Enum
from pathlib import Path
from random import choice

import pygame


class Pipe:
    SPRITE_LENGTH = 64
    COLOR_NEUTRAL = (217, 219, 212, 90)
    CLICK_SOUND_PATH = str(Path('assets', 'click.wav'))

    class Direction(Enum):
        DOWN = 0
        RIGHT = 1
        UP = 2
        LEFT = 3

        def get_sprite_rotate_angle(self):
            return 90 * self.value

        def _get_offset(self, offset):
            members = list(self.__class__)
            index = members.index(self)
            return members[(index + offset) % len(members)]

        def next_clockwise(self):
            return self._get_offset(-1)

        def opposite(self):
            return self._get_offset(2)

        def get_offset_coords(self, x, y):
            if self is self.DOWN:
                y += 1
            elif self is self.UP:
                y -= 1
            elif self is self.RIGHT:
                x += 1
            else:   # self.value == self.LEFT
                x -= 1
            return x, y

    class Kind(Enum):
        STRAIGHT = 'straight'
        BEND = 'bend'

        def path_empty(self):
            return str(Path('assets', f'{self.value}.png'))

        def path_full(self):
            return str(Path('assets', f'{self.value}_full.png'))

    def __init__(self, screen=None, settings=None, x=0, y=0, full=False, color=COLOR_NEUTRAL, direction=None, kind=None):
        self.screen = screen
        self.x = x
        self.y = y
        self.full = full
        self.color = color
        self.settings = settings
        self.surface = None
        self.direction = direction if direction is not None else choice(list(self.Direction))
        self.kind = kind if kind is not None else choice(list(self.Kind))
        self.image_full = pygame.image.load(self.kind.path_full())
        self.image_empty = pygame.image.load(self.kind.path_empty())
        self.ends = {}
        self.update_ends()
        self.click_sound = pygame.mixer.Sound(self.CLICK_SOUND_PATH)

    def update_ends(self):
        self.ends = (
            {self.direction, self.direction.next_clockwise()}
            if self.kind is self.Kind.BEND else
            {self.direction, self.direction.opposite()}
        )

    def pos(self):
        return self.x, self.y

    def rotate(self):
        self.direction = self.direction.next_clockwise()
        self.update_ends()

    def blitme(self):
        image = self.image_full if self.full else self.image_empty
        self.surface = pygame.transform.rotate(image, self.direction.get_sprite_rotate_angle())
        self.surface.convert_alpha()
        background = self.surface.copy()
        background.fill(self.color)
        background.convert_alpha()
        self.screen.blit(background, self.pos())
        self.screen.blit(self.surface, self.pos())

    def handle_click(self):
        self.rotate()
        if self.settings.sound:
            self.click_sound.play()

    def get_connected(self, board, pos_x, pos_y, entry_dir):
        exit_dir = list(self.ends.difference({entry_dir}))[0]
        connected_x, connected_y = exit_dir.get_offset_coords(pos_x, pos_y)
        if connected_x < 0 or connected_y < 0:
            return None, None, connected_x, connected_y

        try:
            next_pipe = board[connected_y][connected_x]
            next_entry_dir = exit_dir.opposite()
            if next_entry_dir not in next_pipe.ends:
                return None, None, connected_x, connected_y
            return next_pipe, next_entry_dir, connected_x, connected_y
        except IndexError:
            return None, None, connected_x, connected_y
