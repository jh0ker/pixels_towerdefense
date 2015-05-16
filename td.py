import pygame, led, sys, os, random
from pygame.locals import *

""" A very simple arcade shooter demo :)
"""

random.seed()

BLACK = pygame.Color(0,0,0)
WHITE = pygame.Color(255, 255, 255)
GREEN = pygame.Color(0, 255, 0)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(0,0,255)

# detect if a serial/USB port is given as argument
hasSerialPortParameter = ( sys.argv.__len__() > 1 )

# use 90 x 20 matrix when no usb port for real display provided
fallbackSize = ( 90, 20 )

if hasSerialPortParameter:
    serialPort = sys.argv[ 1 ]
    print "INITIALIZING WITH USB-PORT: "+serialPort
    ledDisplay = led.teensy.TeensyDisplay( serialPort, fallbackSize )
else:
    print "INITIALIZING WITH SIMULATOR ONLY."
    ledDisplay = led.teensy.TeensyDisplay( None, fallbackSize )

# use same size for sim and real LED panel
size = ledDisplay.size()
simDisplay = led.sim.SimDisplay(size)
screen = pygame.Surface(size)

# every time an alien spawns...
alienFrequency = 5000
alienSpeed = 0.01

alienSpeedFactor = 1.01
alienFrequencyFactor = 1.02

def expandRect(rect, px):
    _rect = pygame.Rect(rect.x - px, rect.y - px, rect.width + px*2, rect.height + px*2);
    return _rect

class Animation:
    def __init__(self):
        self._lastMove = pygame.time.get_ticks()

    def linearMove(self, x, y, speed):
        distance = (pygame.time.get_ticks() - self._lastMove) * speed
        if distance >= 1:
            self._lastMove = pygame.time.get_ticks()
            return self.rect.move(x * distance, y * distance)

        return self.rect

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(os.path.join('sprite', 'cursor.png'))
        self.rect = self.image.get_rect()
        #self.rect = pygame.Rect((0,0), (2,2))

        self.rect.midleft = screen.get_rect().midleft
        self.rect.x = 2

    def move(self, x, y):
        _rect = self.rect.move(x, y).clip(screen.get_rect())
        if _rect.width >= 3 and _rect.height >= 3 and _rect.x >= -1 and  _rect.y >= -1:
            self.rect = self.rect.move(x, y)
            self.rect.height = 4
            self.rect.width = 4

class Alien(pygame.sprite.Sprite, Animation):
    def __init__(self, hp=10.0):
        pygame.sprite.Sprite.__init__(self)
        Animation.__init__(self)

        self.image = pygame.Surface((2, 2))
        self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.midright = screen.get_rect().midright
        
        self.maxhp = hp
        self.hp = hp

        #self.rect.y = random.randint(0, screen.get_rect().height - self.rect.height)

    def update(self, *args):
    
        if self.rect.x <= 20 and self.rect.y == 9:
            _rect = self.linearMove(-1, 0, alienSpeed)
        elif self.rect.x % 12 == 0:
            if self.rect.y < 16:
                _rect = self.linearMove(0, 1, alienSpeed)
            else:
                _rect = self.linearMove(-1, 0, alienSpeed)
        elif self.rect.x % 6 == 0:
            if self.rect.y > 2:
                _rect = self.linearMove(0, -1, alienSpeed)
            else:
                _rect = self.linearMove(-1, 0, alienSpeed)
        else: 
            _rect = self.linearMove(-1, 0, alienSpeed)

        if not _rect.colliderect(screen.get_rect()):
            self.kill(self.maxhp)
        else:
            self.rect = _rect

    def kill(self, damage = 3.34):
        self.hp -= damage
        
        if self.hp <= 0:
            super(Alien, self).kill()
        else:
            percent = float(self.hp) / self.maxhp
            
            if percent < .35:
                self.image.fill(RED)
            elif percent < .68:
                self.image.fill(YELLOW)
            else:
                self.image.fill(GREEN)

class Tower(pygame.sprite.Sprite):
    def __init__(self, cursor):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.midleft = cursor.rect.midleft
        self.rect.x += 1
        
    def update(self, aliens):
        shootrange = expandRect(self.rect, 4);
        t = pygame.sprite.Sprite()
        t.rect = shootrange
        
        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.aaline(screen, BLUE, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5),1)
                alien.kill(.1)
                break
        
class Target(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(pygame.Color(255,255,255))
        self.rect = self.image.get_rect()
        self.rect.midleft = (16, 10)

def main():
    global alienSpeed, alienFrequency

    clock = pygame.time.Clock()

    cursor = Cursor()
    target = Target()
    
    player = pygame.sprite.Group()
    player.add(cursor)
    player.add(target)

    towers = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    

    movementX = 0
    movementY = 0
    lastAlien = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    movementY = -1
                elif event.key == K_DOWN:
                    movementY = 1
                if event.key == K_RIGHT:
                    movementX = 1
                elif event.key == K_LEFT:
                    movementX = -1
                elif event.key == K_SPACE:
                    towers.add(Tower(cursor))

            elif event.type == KEYUP:
                if event.key == K_UP or event.key == K_DOWN:
                    movementY = 0
                elif event.key == K_RIGHT or event.key == K_LEFT:
                    movementX = 0

        cursor.move(movementX, movementY)
        if (pygame.time.get_ticks() - lastAlien) > alienFrequency:
            # spawn new alien :)
            aliens.add(Alien())
            lastAlien = pygame.time.get_ticks()
            alienSpeed *= alienSpeedFactor
            alienFrequency /= alienFrequencyFactor

        # check collisions
        # .. any alien hit?
        pygame.sprite.groupcollide(towers, aliens, True, True)

        # .. player hit?
        targhit = pygame.sprite.spritecollideany(target, aliens)

        if targhit != None:
            screen.fill(RED)
            targhit.kill(1.0)
        else:
            screen.fill(BLACK)

        player.update()
        towers.update(aliens)
        aliens.update()

        towers.draw(screen)
        aliens.draw(screen)
        player.draw(screen)

        simDisplay.update(screen)
        ledDisplay.update(screen)

        clock.tick(30)

main()
