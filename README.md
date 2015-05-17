# pixels_towerdefense
A towerdefense game for the arduino pixels videogame, created during the Videogame Hackathon at Hackerspace Bremen.
It's based on the shooter example from https://github.com/michaelkoetter/pygame-ledpixels

### Objective
Kill Enemies to get Money. Your Money is displayed at the lower left corner, your Lifepoints are displayed at the upper left corner. Each time an Alien (the green squares) gets to your Base (the white square at the end of the track), you loose one Lifepoint. Aliens get stronger, faster and spawn more frequently over time, so be sure to build Towers! If you place a Tower on top of others, the Tower(s) below will be destroyed.  

### Controls
* Arrow keys or Joystick to move the cursor
* Space or Button 1 on the controller to place a Tower
* W or Button 2 on the controller to select a Tower
* Press both the Player 1 and Player 2 buttons on the controller to end the game immediately

### Towers
* Blue: 3 Money, weak, high-range, multiple targets
* Orange: 5 Money, no damage, low-range, slows by 50% (stacks once to 25%), multiple targets
* Cyan: 10 Money, stronger, low-range, single target
* Magenta: 20 Money, strongest, mid-range, single target

There are little colored dots on the Money-meter which mark the amount of Money you need to buy the respective Tower.
