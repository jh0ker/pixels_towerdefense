#!/usr/bin/python
__author__ = 'Jannes Hoeke'

import led
import sys
from Alien import Alien, Path
from Towers import Tower, SlowTower, StrongerTower, StrongestTower
from Colors import *
from pygame.locals import *
from Cursor import Cursor
from Target import Target
import Gamedata

""" https://github.com/jh0ker/pixels_towerdefense
"""

# detect if a serial/USB port is given as argument
hasSerialPortParameter = (sys.argv.__len__() > 1)

fallbackSize = (90, 20)

if hasSerialPortParameter:
    serialPort = sys.argv[1]
    print "INITIALIZING WITH USB-PORT: " + serialPort
    ledDisplay = led.teensy.TeensyDisplay(serialPort, fallbackSize)
else:
    print "INITIALIZING WITH SERVER DISPLAY AND SIMULATOR."
    ledDisplay = led.dsclient.DisplayServerClientDisplay('localhost', 8123, fallbackSize)

# use same size for sim and real LED panel
size = ledDisplay.size()
simDisplay = led.sim.SimDisplay(size)
screen = pygame.Surface(size)

Gamedata.screen = screen

def main():
    # Set local game variables
    towersel = 0
    
    movement_x = 0
    movement_y = 0
    last_alien = 0

    alien_frequency = 200.0
    alien_speed = 20
    alien_hp = 30.0

    alien_hp_factor = 1.1
    alien_speed_add = -1
    alien_frequency_factor = 1.03

    tickcount = 0

    # init
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
    aliens = pygame.sprite.OrderedUpdates()  # Make Aliens ordered so always the first one will be shot at
    
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
    screen.blit(write_lobby, (2, 4))
    
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
                        movement_y = -1
                    elif event.type == KEYDOWN and event.key == K_DOWN or event.type == JOYAXISMOTION and event.axis == 1 and event.value > 0:
                        movement_y = 1
                    elif event.type == KEYDOWN and event.key == K_RIGHT or event.type == JOYAXISMOTION and event.axis == 0 and event.value > 0:
                        movement_x = 1
                    elif event.type == KEYDOWN and event.key == K_LEFT or event.type == JOYAXISMOTION and event.axis == 0 and event.value < 0:
                        movement_x = -1
                        
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
                        
                        if Gamedata.money >= tower.cost:
                            place = True        
                            
                            for p in path:
                                if pygame.sprite.collide_rect(tower, p):
                                    place = False
                            
                            if place:
                                for t in towers:
                                    if pygame.sprite.collide_rect(t, tower):
                                        t.kill()
                                towers.add(tower)
                                Gamedata.money -= tower.cost
                                
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
                        movement_y = 0
                    elif event.type == KEYUP and (event.key == K_RIGHT or event.key == K_LEFT) or event.type == JOYAXISMOTION and event.axis == 0:
                        movement_x = 0
                
            # We tried to process an event that we should not have processed
            except AttributeError:
                print("AttributeError on " + str(event))
        
        cursor.move(movement_x, movement_y)
        
        # Count ticks independently of time so the timings wont fuck up if the CPU is slow
        tickcount += 1
        
        # Spawn Alien and increase difficulty
        if (tickcount - last_alien) > alien_frequency:
            # Spawn new alien :)
            aliens.add(Alien(alien_hp))
            last_alien = tickcount
            alien_hp *= alien_hp_factor
            
            # Some balancing stuff
            if alien_speed > 3:
                alien_speed += alien_speed_add
            
            if alien_frequency > 150:
                alien_frequency /= alien_frequency_factor
                
            if alien_hp_factor > 1.015:
                alien_hp_factor -= 0.002
            elif alien_hp < 1500:
                alien_hp_factor = 1.015
            elif alien_hp >= 1500:
                alien_hp_factor = 1.01
                
            print("Spawned Alien... HP: %6f HP Factor: %6f " % (alien_hp, alien_hp_factor))

        # Alien arrived at Base?
        targhit = pygame.sprite.spritecollideany(target, aliens)

        if targhit is not None:
            screen.fill(RED)
            targhit.kill(targhit.maxhp)
            Gamedata.life -= 1
        else:
            screen.fill(BLACK)
        
        # Draw background
        screen.blit(bg, (0, 0))
        
        # Do updates on all groups
        player.update()
        
        if tickcount % alien_speed == 0:
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
        if Gamedata.money > 0:
            pygame.draw.line(screen, WHITE, (1, screen.get_rect().height - 2), (Gamedata.money, screen.get_rect().height - 2), 1)
            
        if Gamedata.life > 0:
            pygame.draw.line(screen, WHITE, (1, 1), (Gamedata.life, 1), 1)
        
        # Update screen
        simDisplay.update(screen)
        ledDisplay.update(screen)

        if Gamedata.life == 0:
            gameover = 2
    
        # Tick the clock
        clock.tick(30)
        
    # End of the game
    text_gameover = "GAME OVER"
    write_gameover = font_text.render(text_gameover, True, WHITE)
    
    screen.blit(write_gameover, (10, 4))
    
    simDisplay.update(screen)
    ledDisplay.update(screen)
    
    # Wait for keypress
    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
            break
            
    # Show score
    screen.fill(BLACK)
    text_gameover = "Score: " + str(int(Gamedata.score))
    write_gameover = font_text.render(text_gameover, True, WHITE)
    
    screen.blit(write_gameover, (2, 4))
    
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
