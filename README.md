# pixels_towerdefense
A towerdefense game for the arduino pixels videogame, created during the Videogame Hackathon at Hackerspace Bremen.
It's based on the shooter example from https://github.com/michaelkoetter/pygame-ledpixels

Use the arrow keys to move the cursor and press W to select a tower. Kill Enemies to get Money. Your Money is displayed at the lower left corner, your Lifepoints are displayed at the upper left corner. Each time an Enemy gets to the white square at the end of the track, you loose one Lifepoint. Enemies get stronger, faster and spawn more frequently over time, so be sure to upgrade! If you place a Tower on top of another one, the tower(s) below will be destroyed.  

Towers:
* Blue: 3 Money, weakest 
* Cyan: 5 Money, stronger
* Orange: 5 Money, no damage, slows by 50% (does not stack)
* Magenta: 10 Money, strongest, shoots multiple targets at once
