# Go Forth and Butterfly
A Python-based game created for [PyWeek 29](https://pyweek.org/29/)

You are a leader in a rainbow of butterflies,
 taking them on a journey and discovering new skills and challenges along the way
 
## Installation
(to be confirmed)

You can either run the Windows or Linux executable. Or run the Python source code

To run the game using the source code
1. (optional, recommended) Create and activate a virtual environment, with Python 3.6 or higher
1. clone the source code
1. pip install -r requirements.txt
1. python main.py

Optional parameters
* --debug: get some debug information
* --level (number, up to 5): roll forward to the specified level
 
## How to play

Your butterfly will try to stay with the flock, so will speed up, slowdown and turn of its own accord.
Other forces may also affect it. So steering gets quite interesting. It can be a bit frustrating,
but this adds a bit of flavour to the game.

You will start with the following abilities:
* Left and right arrows: push your butterfly to turn left or right
* Up arrow: increase the maximum speed of your butterfly and give it a little push
* Down arrow: decrease the maximum speed
* Space bar: return to the default speed
* Pause the game
* Show a help screen
* Fly through a 'gate' to a new level - but only once you have finished the level
* Return to a previous level

As you visit new levels you will discover new abilities. 
These will stay with you, even if you return to a previous level. 
The help screen will show you all your current abilities.

Other butterflies can always go through a gate to a new level, but they can never go back. 
You can only go to the next level once you have completed the current level, but you *can* go back.

## Known issues
This is as far as I got during the game jam. 
Here are some bugs which were still on the list when I ran out of time

* The screen resolution is fixed at 1840 x 1035 (to fit on a 1920 x 1080 monitor). 
Apologies if that is too large for your screen
* Whilst the game is paused, butterflies no longer move, but the clock keeps running
* Only the butterflies which are on the current level move
* Butterflies seem to be able to fly off the screen and disappear. 
When your butterfly disappears, just wait for it to come back. Others may disappear completely
* When you ask nearby butterflies to land, they can no longer accelerate upwards. 
If they are too low on the screen, they cannot go up to the landing zone, so they just 
wander about at the bottom of the screen
* When going hungry there isn't a lot of time to control the flock and take them to the flowers. 
This needs some fine tuning, so you feel more in control

## Potential enhancements
Provided I don't get distracted by another side project :-), here is how I would like to improve the game

* Fix known issues
* New game mechanism: predators, and luring them away from the flock
* New game mechanism: mating (most of this code is already in place)
* New game mechanism: find things (e.g. seeds), 'inventory'
* Training levels for these new game mechanisms
* Tell a better story, going from screen to screen
* After the 'training levels', create some interesting challenges (puzzles?)
* Map to show complete screens, positions of butterflies (live, i.e. moving), tease coming screens
* And an ability, using the map, to move to any unlocked level
* Save a game in progress
* Parallax levels, so butterflies can fly behind scenery, etc
* Some animations (spritesheet)- flapping wings, shimmering gate
* Show clearer progress towards level goals
* Some sort of scoring, e.g. time spent in a level (faster = better)
* Make the strength of some forces depend on the distance
* Create an executable, e.g. with pyinstaller (I tried, but haven't figured it all out yet)
* Sound
* Speed up code. Currently somewhere between 100 and 200 butterflies it becomes too slow
* Test, tweak, streamline :-)

## Attributions
All resources used are free for commercial use. See details in links below.

* Butterflies from https://pixabay.com/illustrations/butterfly-clip-art-butterflies-4117065/
* Level 1 and 4 backgrounds from https://craftpix.net/freebies/free-cartoon-forest-game-backgrounds/
* Level 2 and 5 background from https://craftpix.net/freebies/free-desert-scrolling-2d-game-backgrounds/
* Level 3 background from https://craftpix.net/freebies/free-cartoon-parallax-2d-backgrounds/
* Font from https://www.fontsquirrel.com/fonts/acme under the SIL Open Font License v1.10. License file in the fonts folder
* Sleeping symbol from https://thenounproject.com/search/?q=sleeping&i=113358, "sleep by Sergey Demushkin from the Noun Project"
* Landing symbol (down arrow) from https://thenounproject.com/search/?q=arrow&i=1920772, "Arrow by Alice Design from the Noun Project"
* Pause (landed) symbol from https://thenounproject.com/search/?q=paused&i=1939967, "pause by Adrien Coquet from the Noun Project"
* Dying symbol (skull) from https://thenounproject.com/search/?q=skull&i=121351, "Skull by Ricardo Moreira from the Noun Project"
* Hungry symbol (flower) from https://thenounproject.com/search/?q=flower&i=3202467, "Flower by Adrien Coquet from the Noun Project"
* Pause, play, Ok and help buttons from https://craftpix.net/freebies/free-jungle-cartoon-2d-game-ui/
