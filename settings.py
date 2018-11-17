import pygame

from pipe import Pipe


class Settings:
    DIFFICULTY_TO_PIPES_OFFSET = 8
    PIPES_X_TO_Y_OFFSET = 2
    SCREEN_PIPE_PADDING = 1
    MAX_DIFFICULTY = 5

    def __init__(self, difficulty=1, sound=False):
        self.difficulty = difficulty
        self.sound = sound

    def y_pipes_num(self):
        return self.difficulty + self.DIFFICULTY_TO_PIPES_OFFSET

    def x_pipes_num(self):
        return self.y_pipes_num() + self.PIPES_X_TO_Y_OFFSET

    def screen_height(self):
        return (self.y_pipes_num() + self.SCREEN_PIPE_PADDING * 2) * Pipe.SPRITE_LENGTH

    def screen_width(self):
        return (self.x_pipes_num() + self.SCREEN_PIPE_PADDING * 2) * Pipe.SPRITE_LENGTH

    def screen_size(self):
        return self.screen_width(), self.screen_height()

    def screen_width_center(self):
        return self.screen_width() / 2

    def screen_height_center(self):
        return self.screen_height() / 2

    def screen_center(self):
        return self.screen_width_center(), self.screen_height_center()
