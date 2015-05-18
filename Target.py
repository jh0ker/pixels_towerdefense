__author__ = 'Jannes Hoeke'

from Colors import *

# The Base which you should defend
class Target(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.midleft = (14, 10)
