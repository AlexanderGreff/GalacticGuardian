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

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

PLAYER_SPEED = 6
MAX_AI_SPEED = 6

def normalised(x, y):
    # Return a unit vector
    # Get length of vector (x,y) - math.hypot uses Pythagoras' theorem to get length of hypotenuse
    # of right-angle triangle with sides of length x and y
    # todo note on safety
    length = math.hypot(x, y)
    return (x / length, y / length)

def sign(x):
    # Returns -1 or 1 depending on whether number is positive or negative
    return -1 if x < 0 else 1

num_players = 1

# Is space currently being held down?
space_down = False


# Pygame Zero calls the update and draw functions each frame

def update():
    global state, game, num_players, space_down

    # Work out whether the space key has just been pressed - i.e. in the previous frame it wasn't down,
    # and in this frame it is.
   

def draw():
    #game.draw()
    screen.blit("bg1.jpg", (0,0))


# The mixer allows us to play sounds and music
# try:
#     pygame.mixer.quit()
#     pygame.mixer.init(44100, -16, 2, 1024)

#     music.play("theme")
#     music.set_volume(0.3)
# except:
#     # If an error occurs (e.g. no sound device), just ignore it
#     pass




# Tell Pygame Zero to start - this line is only required when running the game from an IDE such as IDLE or PyCharm
pgzrun.go()
