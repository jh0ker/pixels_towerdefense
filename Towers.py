__author__ = 'Jannes Hoeke'

from Colors import *
import Gamedata

# used for shooting ranges of towers
def expand_rect(rect, px):
    _rect = pygame.Rect(rect.x - px, rect.y - px, rect.width + px*2, rect.height + px*2)
    return _rect

# Tower classes
class Tower(pygame.sprite.Sprite):
    def __init__(self, cursor):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.midleft = cursor.rect.midleft
        self.rect.x += 1
        self.cost = 3

    def update(self, aliens):
        shootrange = expand_rect(self.rect, 8)
        t = pygame.sprite.Sprite()
        t.rect = shootrange

        hitcounter = 0

        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(Gamedata.screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(.1)

                hitcounter += 1
                if hitcounter == 3:
                    break


class SlowTower(Tower):
    def __init__(self, cursor):
        Tower.__init__(self, cursor)
        self.image.fill(ORANGE)
        self.cost = 5

    def update(self, aliens):
        shootrange = expand_rect(self.rect, 5)
        t = pygame.sprite.Sprite()
        t.rect = shootrange

        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(Gamedata.screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.reduce_speed += 1


class StrongerTower(Tower):
    def __init__(self, cursor):
        Tower.__init__(self, cursor)
        self.image.fill(CYAN)
        self.cost = 10

    def update(self, aliens):
        shootrange = expand_rect(self.rect, 5)
        t = pygame.sprite.Sprite()
        t.rect = shootrange

        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(Gamedata.screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(.8)
                break


class StrongestTower(Tower):
    def __init__(self, cursor):
        Tower.__init__(self, cursor)
        self.image.fill(MAGENTA)
        self.cost = 20

    def update(self, aliens):
        shootrange = expand_rect(self.rect, 7)
        t = pygame.sprite.Sprite()
        t.rect = shootrange

        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(Gamedata.screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(1.8)
                break

