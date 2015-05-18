#!/usr/bin/python

import pygame, led, sys, os
from pygame.locals import *

""" https://github.com/jh0ker/pixels_towerdefense
"""

# Colors
BLACK = pygame.Color(0,0,0)
WHITE = pygame.Color(255, 255, 255)
GREEN = pygame.Color(0, 255, 0)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(0, 0, 255)
CYAN = pygame.Color(0, 255, 255)
MAGENTA = pygame.Color(255, 0, 255)
ORANGE = pygame.Color(255, 140, 0)
LOBBY = pygame.Color(48, 144, 96)

SHOOT = pygame.Color(50, 0, 0)

# detect if a serial/USB port is given as argument
hasSerialPortParameter = ( sys.argv.__len__() > 1 )

fallbackSize = ( 90, 20 )

if hasSerialPortParameter:
    serialPort = sys.argv[ 1 ]
    print "INITIALIZING WITH USB-PORT: "+serialPort
    ledDisplay = led.teensy.TeensyDisplay( serialPort, fallbackSize )
else:
    print "INITIALIZING WITH SERVER DISPLAY AND SIMULATOR."
    ledDisplay = led.dsclient.DisplayServerClientDisplay('localhost', 8123, fallbackSize)

# use same size for sim and real LED panel
size = ledDisplay.size()
simDisplay = led.sim.SimDisplay(size)
screen = pygame.Surface(size)

# init globals
alienFrequency = 0
alienSpeed = 0
alienHp = 0

alienSpeedAdd = -1
alienFrequencyFactor = 1.03
alienHpFactor = 1.1

money = 6
life = 3

score = 0.0

# used for shooting ranges of towers
def expandRect(rect, px):
    _rect = pygame.Rect(rect.x - px, rect.y - px, rect.width + px*2, rect.height + px*2);
    return _rect

# Base class for Aliens
class Animation:
    def linearMove(self, x, y):
        return self.rect.move(x, y)

# The cursor to place towers and to select towers
class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(os.path.join('sprite', 'cursor.png'))
        self.rect = self.image.get_rect()

        self.rect.midleft = screen.get_rect().midleft
        self.rect.x = 2

    def move(self, x, y):
        # Allow cursor to move out of screen by one pixel
        _rect = self.rect.move(x, y).clip(screen.get_rect())
        if _rect.width >= 3 and _rect.height >= 3 and _rect.x >= -1 and  _rect.y >= -1:
            self.rect = self.rect.move(x, y)
            self.rect.height = 4
            self.rect.width = 4

class Alien(pygame.sprite.Sprite, Animation):
    def __init__(self, hp=10.0):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((2, 2))
        self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.midright = screen.get_rect().midright
        
        self.maxhp = hp
        self.hp = hp
        
        self.reduce_speed = 0
        
        # Count how many times an alien was updated for slowing purposes
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
            _rect = self.linearMove(-1, 0)
        elif self.rect.x % 12 == 0:
            if self.rect.y < 16:
                _rect = self.linearMove(0, 1)
            else:
                _rect = self.linearMove(-1, 0)
        elif self.rect.x % 6 == 0:
            if self.rect.y > 2:
                _rect = self.linearMove(0, -1)
            else:
                _rect = self.linearMove(-1, 0)
        else: 
            _rect = self.linearMove(-1, 0)

        self.rect = _rect

    # Override the kill method to implement a damage model
    def kill(self, damage):
        
        global money, score
        self.hp -= damage
        
        if self.hp <= 0:
            super(Alien, self).kill()
            money += 1
            score += self.maxhp
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
        shootrange = expandRect(self.rect, 8);
        t = pygame.sprite.Sprite()
        t.rect = shootrange
        
        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(.1)
                
class SlowTower(Tower):
    def __init__(self, cursor):
        Tower.__init__(self, cursor)
        self.image.fill(ORANGE)
        self.cost = 5
        
    def update(self, aliens):
        shootrange = expandRect(self.rect, 5);
        t = pygame.sprite.Sprite()
        t.rect = shootrange
        
        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.reduce_speed += 1

class StrongerTower(Tower):
    def __init__(self, cursor):
        Tower.__init__(self, cursor)
        self.image.fill(CYAN)
        self.cost = 10
        
    def update(self, aliens):
        shootrange = expandRect(self.rect, 5);
        t = pygame.sprite.Sprite()
        t.rect = shootrange
        
        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(.8)
                break

class StrongestTower(Tower):
    def __init__(self, cursor):
        Tower.__init__(self, cursor)
        self.image.fill(MAGENTA)
        self.cost = 20
        
    def update(self, aliens):
        shootrange = expandRect(self.rect, 7);
        t = pygame.sprite.Sprite()
        t.rect = shootrange
        
        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.line(screen, SHOOT, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(1.8)
                break

# The Base which you should defend
class Target(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.midleft = (14, 10)

def main():
    global alienSpeed, alienFrequency, alienHp, alienHpFactor, money, life, score

    # (Re)set game variables
    towersel = 0
    
    movementX = 0
    movementY = 0
    lastAlien = 0
    
    money = 6
    life = 3
    
    alienFrequency = 200.0
    alienSpeed = 20
    alienHp = 30.0
    alienHpFactor = 1.1
    
    score = 0.0
    
    tickcount = 0

    # inits
    clock = pygame.time.Clock()
    pygame.joystick.init()
    
    # Initialize first joystick
    if pygame.joystick.get_count() > 0:
        stick = pygame.joystick.Joystick(0)
        stick.init()
        
    # Stuff that belongs to the player
    cursor = Cursor()
    target = Target()
    
    player = pygame.sprite.Group()
    player.add(cursor)
    player.add(target)
    
    # Other sprite groups
    towers = pygame.sprite.Group()
    aliens = pygame.sprite.OrderedUpdates() # Make Aliens ordered so always the first one will be shot at
    
    # Set up background
    bg = pygame.Surface(size)
    bg.fill(BLACK)
    bg.set_colorkey(BLACK)
    
    # The path
    path = pygame.sprite.Group()
    
    for c in range(227):
        tile = Path()
        for c2 in range(c):
            tile.update()
        path.add(tile)
        
    path.draw(bg)
    
    # The Towers for selection and dots on the money-meter
    menu = pygame.sprite.Group()
    towcurs = Cursor()
    
    towcurs.move(-2, 5)
    menu.add(Tower(towcurs))
    bg.set_at((3, 18), BLUE)
    
    towcurs.move(3, 0)
    menu.add(SlowTower(towcurs))
    bg.set_at((5, 18), ORANGE)
    
    towcurs.move(3, 0)
    menu.add(StrongerTower(towcurs))
    bg.set_at((10, 18), CYAN)
    
    towcurs.move(3, 0)
    menu.add(StrongestTower(towcurs))
    bg.set_at((20, 18), MAGENTA)
    
    menu.draw(bg)
    
    # Reset Tower Cursor for later use
    towcurs.move(-9, 0)
    player.add(towcurs)
    
    gameover = 0
    
    # Show lobby message
    pygame.font.init()
    font_text = pygame.font.SysFont(None, 18)
    
    text_lobby = "Towerdefense!"
    write_lobby = font_text.render(text_lobby, True, LOBBY)
    
    screen.fill(BLACK)
    screen.blit(write_lobby, (2,4))
    
    simDisplay.update(screen)
    ledDisplay.update(screen)
    
    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
            break
    
    
    while gameover < 2:
        gameover = 0
        
        # Process event queue
        for event in pygame.event.get():
            try:
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Keypresses on keyboard and joystick axis motions / button presses
                elif event.type == KEYDOWN or event.type == JOYAXISMOTION and event.value != 0 or event.type == JOYBUTTONDOWN:
                    # Movements
                    if event.type == KEYDOWN and event.key == K_UP or event.type == JOYAXISMOTION and event.axis == 1 and event.value < 0:
                        movementY = -1
                    elif event.type == KEYDOWN and event.key == K_DOWN or event.type == JOYAXISMOTION and event.axis == 1 and event.value > 0:
                        movementY = 1
                    elif event.type == KEYDOWN and event.key == K_RIGHT or event.type == JOYAXISMOTION and event.axis == 0 and event.value > 0:
                        movementX = 1
                    elif event.type == KEYDOWN and event.key == K_LEFT or event.type == JOYAXISMOTION and event.axis == 0 and event.value < 0:
                        movementX = -1
                        
                    # Tower selection
                    elif event.type == KEYDOWN and event.key == K_w or event.type == JOYBUTTONDOWN and event.button == 2:
                        towersel += 1
                        towcurs.move(3, 0)
                        
                        if towersel > 3:
                            towersel = 0
                            towcurs.move(-12, 0)
                            
                    # Tower placement
                    elif event.type == KEYDOWN and event.key == K_SPACE or event.type == JOYBUTTONDOWN and event.button == 1:
                        if towersel == 0:
                            tower = Tower(cursor)
                        elif towersel == 1:
                            tower = SlowTower(cursor)
                        elif towersel == 2:
                            tower = StrongerTower(cursor)
                        elif towersel == 3:
                            tower = StrongestTower(cursor)
                        
                        if money >= tower.cost:
                            place = True        
                            
                            for p in path:
                                if pygame.sprite.collide_rect(tower, p):
                                    place = False
                            
                            if place:
                                for t in towers:
                                    if pygame.sprite.collide_rect(t, tower):
                                        t.kill()
                                towers.add(tower)
                                money -= tower.cost
                                
                    # If both player buttons on the controller or ESC on the keyboard are pressed, end the game
                    elif event.type == JOYBUTTONDOWN and event.button == 7:
                        gameover += 1
                    elif event.type == JOYBUTTONDOWN and event.button == 8:
                        gameover += 1
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        gameover = 2

                # Stop cursor movement in case of keyup or axis move to home position
                elif event.type == KEYUP or event.type == JOYAXISMOTION and event.value == 0.0:
                    if event.type == KEYUP and (event.key == K_UP or event.key == K_DOWN) or event.type == JOYAXISMOTION and event.axis == 1:
                        movementY = 0
                    elif event.type == KEYUP and (event.key == K_RIGHT or event.key == K_LEFT) or event.type == JOYAXISMOTION and event.axis == 0:
                        movementX = 0
                
            # We tried to process an event that we should not have processed
            except AttributeError:
                print("AttributeError on " + str(event))
        
        cursor.move(movementX, movementY)
        
        # Count ticks independently of time so the timings wont fuck up if the CPU is slow
        tickcount += 1
        
        # Spawn Alien and increase difficulty
        if (tickcount - lastAlien) > alienFrequency:
            # Spawn new alien :)
            aliens.add(Alien(alienHp))
            lastAlien = tickcount
            alienHp *= alienHpFactor
            
            # Some balancing stuff
            if alienSpeed > 3:
                alienSpeed += alienSpeedAdd
            
            if alienFrequency > 150:
                alienFrequency /= alienFrequencyFactor
                
            if alienHpFactor > 1.015:
                alienHpFactor -= 0.002
            elif alienHp < 1500:
                alienHpFactor = 1.015
            elif alienHp >= 1500:
                alienHpFactor = 1.01
                
            print("Spawned Alien... HP: %6f HP Factor: %6f " % (alienHp, alienHpFactor))

        # Alien arrived at Base?
        targhit = pygame.sprite.spritecollideany(target, aliens)

        if targhit != None:
            screen.fill(RED)
            targhit.kill(targhit.maxhp)
            life -= 1
        else:
            screen.fill(BLACK)
        
        # Draw background
        screen.blit(bg, (0,0))
        
        # Do updates on all groups
        player.update()
        
        if tickcount % alienSpeed == 0:
            aliens.update()
        else:
            for alien in aliens:
                alien.reduce_speed = 0
        
        towers.update(aliens)
        
        # Draw all groups
        towers.draw(screen)
        aliens.draw(screen)
        player.draw(screen)
        
        # Draw money and life bar
        if money > 0:
            pygame.draw.line(screen, WHITE, (1, screen.get_rect().height - 2), (money, screen.get_rect().height - 2), 1)
            
        if life > 0:
            pygame.draw.line(screen, WHITE, (1, 1), (life, 1), 1)
        
        # Update screen
        simDisplay.update(screen)
        ledDisplay.update(screen)

        if life == 0:
            gameover = 2
    
        # Tick the clock
        clock.tick(30)
        
    # End of the game
    text_gameover = "GAME OVER"
    write_gameover = font_text.render(text_gameover, True, WHITE)
    
    screen.blit(write_gameover, (10,4))
    
    simDisplay.update(screen)
    ledDisplay.update(screen)
    
    # Wait for keypress
    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
            break
            
    # Show score
    screen.fill(BLACK)
    text_gameover = "Score: " + str(int(score))
    write_gameover = font_text.render(text_gameover, True, WHITE)
    
    screen.blit(write_gameover, (2,4))
    
    simDisplay.update(screen)
    ledDisplay.update(screen)
    
    # Wait for keypress
    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
            break
    # Restart game
    # main()
    
main()
