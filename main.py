import pgzero, pgzrun, pygame
import math, sys, random
from enum import Enum
import random

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

game=None

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

class EnemyShip(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self):
        super().__init__("enemyship1")
        self.x = random.randrange(0, WIDTH)
        self.y =  20
        self.shipspeed=5
        self.halfheight=self.height/2
        self.count=0
        self.movex=0
        self.movey=0
        self.minDistance = self.width // 2

    def controls(self):
        if (self.count % 10 == 0):
            xmin = random.randrange(2, 10)
            self.movex = random.randrange(-xmin, xmin)
            self.movey = random.randrange(0, 3)
        self.count+=1
        return self.movex, self.movey

    def isHit(self, item):
        minDist = max(item.minDistance, self.minDistance)
        return self.distance_to(item) < minDist

    def destroyed(self):
        game.enemies.remove(self)
        sounds.explosion.play()

    def update(self):
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y+movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy>=(self.halfheight) and newy<=(HEIGHT-self.halfheight):
            self.y=newy
        else:
            game.enemies.remove(self)

class Bullet(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self,x,y):
        super().__init__("bullet15")
        self.x = x
        self.y = y
        self.speed=5
        self.minDistance = self.width // 2
        #print(self.minDistance)

    def controls(self):
        movex = 0
        movey = self.speed
        return movex,movey
    
    def update(self):
        if game.enemies.checkIsHit(self):
            game.bullets.remove(self)
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y-movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy>=(0) and newy<=(HEIGHT):
            self.y=newy
        else:
            game.bullets.remove(self)

class Spaceship(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self):
        super().__init__("spaceshipsmall")
        shipheight=self.height
        self.x = WIDTH //2
        self.y = HEIGHT - shipheight
        self.shipspeed=5
        self.halfheight=self.height/2
        self.count=0
        self.isDead=False
        self.isDeadCount=0
        self.minDistance = self.width // 2

    def controls(self):
        movex = 0
        movey = 0
        if keyboard.s or keyboard.down:
            movey = self.shipspeed
        elif keyboard.w or keyboard.up:
            movey = -self.shipspeed

        if keyboard.space:
            if self.count % 10 == 0:
                self.fire()
            self.count+=1

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
        if self.isDead and (game.count - self.isDeadCount) % 100 == 0:
            self.isDead = False
        if not self.isDead and game.enemies.checkIsHit(self):
            self.destroyed()

    def fire(self):
        game.bullets.add(Bullet(self.x, self.y-self.halfheight))

    def destroyed(self):
        sounds.spaceshipexplosion.play()
        self.isDead=True
        self.isDeadCount=game.count

    def draw(self):
        if not self.isDead:
            super().draw()  

class Container(object):
    """
    handles all collections of objects in the game
    """
    def __init__(self):
        self.all={}
        self.dead=[]

    def add(self, item):
        self.all[id(item)]=item

    def remove(self, item):
        self.dead.append(item)

    def allItems(self):
        return self.all.values()

    def draw(self):
        for element in self.all.values():
            element.draw()    

    def update(self):
        for item in self.dead:
            self.all.pop(id(item), None)
        if len(self.dead)>0:
            self.dead.clear()
        for element in self.all.values():
            element.update()

class Bullets(Container):
    """
    handles all bullets in the game
    """
    def __init__(self):
        super().__init__()

class Enemies(Container):
    """
    handles all enemies in the game
    """
    def __init__(self):
        super().__init__()

    def checkIsHit(self, item):
        isHit=False
        for enemy in game.enemies.allItems():
            #print(self.distance_to(enemy))
            if enemy.isHit(item):
                enemy.destroyed()
                isHit=True
        return isHit

class Game(object):
    """
    handles all objects in the game
    """
    def __init__(self):
        self.background=Background()
        self.spaceship=Spaceship()
        self.enemies=Enemies()
        self.bullets=Bullets()
        self.count=0

    def draw(self):
        self.background.draw()
        self.spaceship.draw()
        self.enemies.draw()
        self.bullets.draw()

    def playMusic(self):
        music.play("theme")
        music.set_volume(0.3)

    def update(self):
        self.background.update()
        self.spaceship.update()
        self.enemies.update()
        self.bullets.update()
        self.addEnemies()
        self.count+=1
        
    def addEnemies(self):
        if self.count % 100 == 0:
            self.enemies.add(EnemyShip())

game = Game()

#Pygame main loop
# Pygame Zero calls the update and draw functions each frame


# if player.status == 1: screen.draw.text("GAME OVER" , center=(300, 434), owidth=0.5, ocolor=(255,255,255), color=(255,64,0) , fontsize=40)

#we do all of the necessary calcuations in here
def update():
    game.update()

#here we redraw everything     
def draw():
    game.draw()

# The mixer allows us to play sounds and music
try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)

    game.playMusic()

except:
    # If an error occurs (e.g. no sound device), just ignore it
    pass

# Tell Pygame Zero to start - this line is only required when running the game from an IDE such as IDLE or PyCharm
pgzrun.go()
