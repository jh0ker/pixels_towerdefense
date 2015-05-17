import pygame, led, sys, os, random
from pygame.locals import *

""" A very simple arcade shooter demo :)
"""

BLACK = pygame.Color(0,0,0)
WHITE = pygame.Color(255, 255, 255)
GREEN = pygame.Color(0, 255, 0)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(0, 0, 255)
CYAN = pygame.Color(0, 255, 255)
MAGENTA = pygame.Color(255, 0, 255)
ORANGE = pygame.Color(255, 140, 0)

# detect if a serial/USB port is given as argument
hasSerialPortParameter = ( sys.argv.__len__() > 1 )

# use 90 x 20 matrix when no usb port for real display provided
fallbackSize = ( 90, 20 )

if hasSerialPortParameter:
    serialPort = sys.argv[ 1 ]
    print "INITIALIZING WITH USB-PORT: "+serialPort
    ledDisplay = led.teensy.TeensyDisplay( serialPort, fallbackSize )
else:
    print "INITIALIZING WITH DisplayServerClientDisplay AND SIMULATOR."
    ledDisplay = led.dsclient.DisplayServerClientDisplay('localhost', 8123, fallbackSize)

# use same size for sim and real LED panel
size = ledDisplay.size()
simDisplay = led.sim.SimDisplay(size)
screen = pygame.Surface(size)

# every time an alien spawns...
alienFrequency = 5000
alienSpeed = 200
alienHp = 30.0

alienSpeedAdd = -5
alienFrequencyFactor = 1.03
alienHpFactor = 1.1

money = 6
life = 3

score = 0.0


def expandRect(rect, px):
    _rect = pygame.Rect(rect.x - px, rect.y - px, rect.width + px*2, rect.height + px*2);
    return _rect

class Animation:
    def linearMove(self, x, y):
        return self.rect.move(x, y)

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

        self.image = pygame.Surface((2, 2))
        self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.midright = screen.get_rect().midright
        
        self.maxhp = hp
        self.hp = hp
        
        self.reduce_speed = 0
        
        self.updates = 0 

        #self.rect.y = random.randint(0, screen.get_rect().height - self.rect.height)

    def update(self, *args):
        
        self.updates += 1
        
        if self.reduce_speed > 3:
            self.reduce_speed = 3
        
        slow_factor = 1 if self.reduce_speed == 0 else 2 * self.reduce_speed
        if self.updates % slow_factor != 0:
            self.reduce_speed = 0
            return
        
        self.reduce_speed = 0
        
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

    def kill(self, damage = 3.34):
        
        global money, score
        self.hp -= damage
        
        if self.hp <= 0:
            super(Alien, self).kill()
            money += 1
            score += self.maxhp
        else:
            percent = float(self.hp) / self.maxhp
            
            if percent < .35:
                self.image.fill(RED)
            elif percent < .68:
                self.image.fill(YELLOW)
            else:
                self.image.fill(GREEN)

class Path(Alien):
    def __init__(self):
        Alien.__init__(self)
        self.image.fill(pygame.Color(50, 50, 50))
        
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
                pygame.draw.aaline(screen, BLUE, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(.15)
                
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
                pygame.draw.aaline(screen, ORANGE, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
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
                pygame.draw.aaline(screen, CYAN, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
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
        
        hits = 0
        for alien in aliens:
            targhit = pygame.sprite.collide_circle(t, alien)
            if targhit:
                pygame.draw.aaline(screen, MAGENTA, (self.rect.x + .5, self.rect.y + .5), (alien.rect.x + .5, alien.rect.y + .5), 1)
                alien.kill(1.8)
                break
                #hits += 1

class Target(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.midleft = (14, 10)

def main():
    global alienSpeed, alienFrequency, alienHp, alienHpFactor, money, life, score

    clock = pygame.time.Clock()
    pygame.joystick.init()
    
    if pygame.joystick.get_count() > 0:
        stick = pygame.joystick.Joystick(0)
        stick.init()
    else:
        stick = None

    cursor = Cursor()
    target = Target()
    
    player = pygame.sprite.Group()
    player.add(cursor)
    player.add(target)

    towers = pygame.sprite.Group()
    aliens = pygame.sprite.OrderedUpdates()
    
    towersel = 0
    
    movementX = 0
    movementY = 0
    lastAlien = 0
    
    #reset game
    money = 6
    life = 3
    
    alienFrequency = 5000.0
    alienSpeed = 200
    alienHp = 25.0
    alienHpFactor = 1.1
    
    score = 0.0
    
    # Set up background
    bg = pygame.Surface(size)
    bg.fill(BLACK)
    bg.set_colorkey(BLACK)
    
    path = pygame.sprite.Group()
    
    for c in range(227):
        tile = Path()
        for c2 in range(c):
            tile.update()
        path.add(tile)
        
    path.draw(bg)
    
    menu = pygame.sprite.Group()
    towcurs = Cursor()
    
    towcurs.move(-2, 5)
    
    t = Tower(towcurs)
    menu.add(t)
    
    towcurs.move(3, 0)
    
    t = SlowTower(towcurs)
    menu.add(t)
    
    towcurs.move(3, 0)
    
    t = StrongerTower(towcurs)
    menu.add(t)
    
    towcurs.move(3, 0)
    
    t = StrongestTower(towcurs)
    menu.add(t)
    
    towcurs.move(-9, 0)
    
    menu.draw(bg)
    
    player.add(towcurs)

    while True:

        for event in pygame.event.get():
            try:
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == KEYDOWN or event.type == JOYAXISMOTION and event.value != 0 or event.type == JOYBUTTONDOWN:
                    if event.type == KEYDOWN and event.key == K_UP or event.type == JOYAXISMOTION and event.axis == 1 and event.value < 0:
                        movementY = -1
                    elif event.type == KEYDOWN and event.key == K_DOWN or event.type == JOYAXISMOTION and event.axis == 1 and event.value > 0:
                        movementY = 1
                    elif event.type == KEYDOWN and event.key == K_RIGHT or event.type == JOYAXISMOTION and event.axis == 0 and event.value > 0:
                        movementX = 1
                    elif event.type == KEYDOWN and event.key == K_LEFT or event.type == JOYAXISMOTION and event.axis == 0 and event.value < 0:
                        movementX = -1
                        
                    elif event.type == KEYDOWN and event.key == K_w or event.type == JOYBUTTONDOWN and event.button == 2:
                        towersel += 1
                        towcurs.move(3, 0)
                        
                        if towersel > 3:
                            towersel = 0
                            towcurs.move(-12, 0)
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
                            for t in towers:
                                if pygame.sprite.collide_rect(t, tower):
                                    t.kill()
                            
                            place = True        
                            
                            for p in path:
                                if pygame.sprite.collide_rect(tower, p):
                                    place = False
                            
                            if place:
                                towers.add(tower)
                                money -= tower.cost

                elif event.type == KEYUP or event.type == JOYAXISMOTION and event.value == 0.0:
                    if event.type == KEYUP and (event.key == K_UP or event.key == K_DOWN) or event.type == JOYAXISMOTION and event.axis == 1:
                        movementY = 0
                    elif event.type == KEYUP and (event.key == K_RIGHT or event.key == K_LEFT) or event.type == JOYAXISMOTION and event.axis == 0:
                        movementX = 0
                
            except AttributeError:
                print("AttributeError on " + str(event))
                
        cursor.move(movementX, movementY)
        
        # increase difficulty
        if (pygame.time.get_ticks() - lastAlien) > alienFrequency:
            # spawn new alien :)
            aliens.add(Alien(alienHp))
            lastAlien = pygame.time.get_ticks()
            alienHp *= alienHpFactor
            
            if alienSpeed > 60:
                alienSpeed += alienSpeedAdd
            
            if alienFrequency > 1750:
                alienFrequency /= alienFrequencyFactor
                
            if alienHpFactor > 1.005:
                alienHpFactor -= 0.00275
                
            print("Spawned Alien... HP: %6f Speed: %3i Freq: %6f" % (alienHp, alienSpeed, alienFrequency))

        # .. player hit?
        targhit = pygame.sprite.spritecollideany(target, aliens)

        if targhit != None:
            screen.fill(RED)
            targhit.kill(targhit.maxhp)
            life -= 1
        else:
            screen.fill(BLACK)
        
        screen.blit(bg, (0,0))
        
        player.update()
        
        if pygame.time.get_ticks() % alienSpeed <= 30:
            aliens.update()
        else:
            for alien in aliens:
                alien.reduce_speed = 0
        
        towers.update(aliens)
        
        towers.draw(screen)
        aliens.draw(screen)
        player.draw(screen)
        
        #draw money bar
        if money > 0:
            pygame.draw.aaline(screen, WHITE, (1, screen.get_rect().height - 2), (money + 1, screen.get_rect().height - 2),1)
            
        if life > 0:
            pygame.draw.aaline(screen, WHITE, (1, 1), (life + 1, 1),1)
        
        simDisplay.update(screen)
        ledDisplay.update(screen)

        clock.tick(30)
        if life == 0:
            break
    
    pygame.font.init()
    font_text = pygame.font.SysFont(None, 18)
    text_gameover = "GAME OVER"
    write_gameover = font_text.render(text_gameover, True, WHITE)
    
    screen.blit(write_gameover, (10,4))
    
    simDisplay.update(screen)
    ledDisplay.update(screen)
    
    while True:
        event = pygame.event.wait()
        break
            
    screen.fill(BLACK)
    text_gameover = "Score: " + str(int(score))
    write_gameover = font_text.render(text_gameover, True, WHITE)
    
    screen.blit(write_gameover, (2,4))
    
    simDisplay.update(screen)
    ledDisplay.update(screen)
    
    while True:
        event = pygame.event.wait()
        break
    
    main()
    
main()
