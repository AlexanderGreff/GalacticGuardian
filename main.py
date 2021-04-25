import pgzero, pgzrun, pygame
import math, sys, random
from enum import Enum

# Check Python version number. sys.version_info gives version as a tuple, e.g. if (3,7,2,'final',0) for version 3.7.2.
# Unlike many languages, Python can compare two tuples in the same way that you can compare numbers.
if sys.version_info < (3,5):
    print("This game requires at least version 3.5 of Python. Please download it from www.python.org")
    sys.exit()

# Check Pygame Zero version. This is a bit trickier because Pygame Zero only lets us get its version number as a string.
# So we have to split the string into a list, using '.' as the character to split on. We convert each element of the
# version number into an integer - but only if the string contains numbers and nothing else, because it's possible for
# a component of the version to contain letters as well as numbers (e.g. '2.0.dev0')
# We're using a Python feature called list comprehension - this is explained in the Bubble Bobble/Cavern chapter.
pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split('.')]
if pgzero_version < [1,2]:
    print("This game requires at least version 1.2 of Pygame Zero. You have version {0}. Please upgrade using the command 'pip3 install --upgrade pgzero'".format(pgzero.__version__))
    sys.exit()

# Set up constants
WIDTH = 720
HEIGHT = 720
TITLE = "Galactic Guardian"

#defines the center of the screen
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

# PLAYER_SPEED = 6
# MAX_AI_SPEED = 6

# def normalised(x, y):
#     # Return a unit vector
#     # Get length of vector (x,y) - math.hypot uses Pythagoras' theorem to get length of hypotenuse
#     # of right-angle triangle with sides of length x and y
#     # todo note on safety
#     length = math.hypot(x, y)
#     return (x / length, y / length)

def sign(x):
    # Returns -1 or 1 depending on whether number is positive or negative
    return -1 if x < 0 else 1



class Background(object):
    """
    handles logic for scrolling background
    """
    def __init__(self):
        """
        constructor
        """
        self.MAX_IMAGE_Y = 1044
        self.PIXEL_SCROLL = 5
        self.dy1 = 0
        self.dy2 = -self.MAX_IMAGE_Y

    def draw(self):
        screen.blit("bg1", (0, self.dy1))
        screen.blit("bg2", (0, self.dy2))

    def update(self):    
        self.dy1 = self.dy1 + self.PIXEL_SCROLL
        self.dy2 = self.dy2 + self.PIXEL_SCROLL
        
        if self.dy1 >= self.MAX_IMAGE_Y:
            self.dy1 = -self.MAX_IMAGE_Y
        if self.dy2 >= self.MAX_IMAGE_Y:
            self.dy2 = -self.MAX_IMAGE_Y


scrollingbackground=Background()
class EnemyShip(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self):
        super().__init__("enemyship1")
        shipheight=self.height
        self.x = HALF_WIDTH
        self.y =  HALF_HEIGHT
        self.shipspeed=5
        self.halfheight=self.height/2

    def controls(self):
        movex = 0
        movey = 0
        return movex,movey
    
    def update(self):
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y+movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy>=(self.halfheight) and newy<=(HEIGHT-self.halfheight):
            self.y=newy

enemyShip = EnemyShip()

class Bullet(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self):
        super().__init__("bullet15")
        shipheight=self.height
        self.x = HALF_WIDTH
        self.y =  HALF_HEIGHT+70
        self.shipspeed=5
        self.halfheight=self.height/2

    def controls(self):
        movex = 0
        movey = 0
        return movex,movey
    
    def update(self):
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y+movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy>=(self.halfheight) and newy<=(HEIGHT-self.halfheight):
            self.y=newy

bullet = Bullet()
class Spaceship(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self):
        super().__init__("spaceshipsmall")
        shipheight=self.height
        self.x = HALF_WIDTH
        self.y = HEIGHT - shipheight
        self.shipspeed=5
        self.halfheight=self.height/2

    def controls(self):
        movex = 0
        movey = 0
        if keyboard.s or keyboard.down:
            movey = self.shipspeed
        elif keyboard.w or keyboard.up:
            movey = -self.shipspeed
        
        if keyboard.a or keyboard.left:
            movex = -self.shipspeed
        elif keyboard.d or keyboard.right:
            movex = self.shipspeed
        return movex,movey
    
    def update(self):
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y+movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy>=(self.halfheight) and newy<=(HEIGHT-self.halfheight):
            self.y=newy

spaceship=Spaceship()

#Pygame main loop
# Pygame Zero calls the update and draw functions each frame

#we do all of the necessary calcuations in here
def update():
    scrollingbackground.update()
    spaceship.update()
    enemyShip.update()
    bullet.update()

#here we redraw everything     
def draw():
    scrollingbackground.draw()
    spaceship.draw()
    enemyShip.draw()    
    bullet.draw()

# The mixer allows us to play sounds and music
try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)

    music.play("theme")
    music.set_volume(0.3)
except:
    # If an error occurs (e.g. no sound device), just ignore it
    pass


# Create a new Game object, without any players
# game = Game()

# Tell Pygame Zero to start - this line is only required when running the game from an IDE such as IDLE or PyCharm
pgzrun.go()
