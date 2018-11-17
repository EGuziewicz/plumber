import pygame

DEFAULT_FONT = 'freesansbold.ttf'
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def blit_text(text, center_pos, screen, size=50, color=BLACK, bg_color=WHITE):
    large_text = pygame.font.Font(DEFAULT_FONT, size)
    text_surf = large_text.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.center = center_pos

    background = text_surf.copy()
    background.convert_alpha()
    background.fill(bg_color)

    screen.blit(background, text_rect)
    screen.blit(text_surf, text_rect)
    return text_rect
