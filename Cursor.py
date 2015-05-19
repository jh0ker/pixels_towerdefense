__author__ = 'Jannes Hoeke'

import os
from Colors import *
import Gamedata

# The cursor to place towers and to select towers
class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(os.path.join('sprite', 'cursor.png'))
        self.rect = self.image.get_rect()

        self.rect.center = Gamedata.screen.get_rect().center

    def move(self, x, y):
        # Allow cursor to move out of screen by one pixel
        _rect = self.rect.move(x, y).clip(Gamedata.screen.get_rect())
        if _rect.width >= 3 and _rect.height >= 3 and _rect.x >= -1 and  _rect.y >= -1:
            self.rect = self.rect.move(x, y)
            self.rect.height = 4
            self.rect.width = 4
