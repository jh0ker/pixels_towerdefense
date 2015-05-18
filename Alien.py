__author__ = 'Jannes Hoeke'

from Colors import *
import Gamedata

# Base class for Aliens
class Animation:
    def __init__(self):
        pass

    def linear_move(self, x, y):
        return self.rect.move(x, y)


class Alien(pygame.sprite.Sprite, Animation):
    def __init__(self, hp=10.0):
        super(Alien, self).__init__()
        super(pygame.sprite.Sprite, self).__init__()

        self.image = pygame.Surface((2, 2))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.midright = Gamedata.screen.get_rect().midright
        self.maxhp = hp
        self.hp = hp
        self.reduce_speed = 0
        self.updates = 0

    def update(self, *args):

        self.updates += 1

        # Allow a maximum of 75% speed reduce
        if self.reduce_speed > 2:
            self.reduce_speed = 2

        slow_factor = 1 if self.reduce_speed == 0 else 2 * self.reduce_speed
        if self.updates % slow_factor != 0:
            self.reduce_speed = 0
            return

        self.reduce_speed = 0

        # The path the alien walks
        if self.rect.x <= 20 and self.rect.y == 9:
            _rect = self.linear_move(-1, 0)
        elif self.rect.x % 12 == 0:
            if self.rect.y < 16:
                _rect = self.linear_move(0, 1)
            else:
                _rect = self.linear_move(-1, 0)
        elif self.rect.x % 6 == 0:
            if self.rect.y > 2:
                _rect = self.linear_move(0, -1)
            else:
                _rect = self.linear_move(-1, 0)
        else:
            _rect = self.linear_move(-1, 0)

        self.rect = _rect

    # Override the kill method to implement a damage model
    def kill(self, damage):

        self.hp -= damage

        if self.hp <= 0:
            super(Alien, self).kill()
            Gamedata.money += 1
            Gamedata.score += self.maxhp
        else:
            percent = float(self.hp) / self.maxhp

            if percent < .33:
                self.image.fill(RED)
            elif percent < .67:
                self.image.fill(YELLOW)
            else:
                self.image.fill(GREEN)


# Subclass of alien with a different color which is used for the pathway
class Path(Alien):
    def __init__(self):
        Alien.__init__(self)
        self.image.fill(pygame.Color(50, 50, 50))

