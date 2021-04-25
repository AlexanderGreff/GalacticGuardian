import pgzero, pgzrun, pygame
import math, sys, random
from enum import Enum
import random
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


class Mode(Enum):
    GameOver = 1
    Play = 2

mode = Mode.GameOver
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
    def __init__(self, game, scrollSpeed=5):
        """
        constructor
        """
        self.MAX_IMAGE_Y = 1044
        self.PIXEL_SCROLL = scrollSpeed
        self.dy1 = 0
        self.dy2 = -self.MAX_IMAGE_Y
        self.game = game

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
    def __init__(self,game):
        if random.randrange(1,3) == 1:
            super().__init__("enemyship1")  
        else:
            super().__init__("enemyblue2")  
        self.x = random.randrange(0, WIDTH)
        self.y =  20
        self.shipspeed=5
        self.halfheight=self.height/2
        self.movex=0
        self.movey=0
        self.minDistance = self.width // 2
        self.game = game

    def controls(self):
        if (self.game.count % 10 == 0):
            xmin = random.randrange(2, 10)
            self.movex = random.randrange(-xmin, xmin)
            self.movey = random.randrange(0, 3)
        return self.movex, self.movey

    def isHit(self, item):
        minDist = max(item.minDistance, self.minDistance)
        return self.distance_to(item) < minDist

    def destroyed(self):
        self.game.scoreBoard.incScore()
        self.game.enemies.remove(self)
        sounds.explosion.play()

    def update(self):
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y+movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy >= 0 and newy<=(HEIGHT-self.halfheight):
            self.y=newy
        else:
            self.game.enemies.remove(self)

class Bullet(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self,game,x,y):
        super().__init__("bullet15")
        self.x = x
        self.y = y
        self.speed=5
        self.minDistance = self.width // 2
        self.game = game
        #print(self.minDistance)

    def controls(self):
        movex = 0
        movey = self.speed
        return movex,movey
    
    def update(self):
        if self.game.enemies.checkIsHit(self):
            self.game.bullets.remove(self)
        movex,movey=self.controls()
        newx=self.x+movex
        newy=self.y-movey
        if newx>=0 and newx<=WIDTH:         
            self.x=newx
        if newy>=(0) and newy<=(HEIGHT):
            self.y=newy
        else:
            self.game.bullets.remove(self)

class Spaceship(Actor):
    """
    handles logic for scrolling background
    """
    def __init__(self,game):
        super().__init__("spaceshipsmall")
        shipheight=self.height
        self.x = WIDTH //2
        self.y = HEIGHT - shipheight
        self.shipspeed=5
        self.halfheight=self.height/2
        self.countFire=0
        self.isDead=False
        self.isDeadCount=0
        self.minDistance = self.width // 2
        self.game = game

    def controls(self):
        movex = 0
        movey = 0
        if not self.isDead:
            if keyboard.s or keyboard.down:
                movey = self.shipspeed
            elif keyboard.w or keyboard.up:
                movey = -self.shipspeed
                sounds.engineshort.play()

            if keyboard.space:
                if self.countFire % 10 == 0:
                    self.fire()
                self.countFire+=1

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
        if self.isDead and (self.game.count - self.isDeadCount) % 100 == 0:
            self.isDead = False
        if not self.isDead and self.game.enemies.checkIsHit(self):
            self.destroyed()

    def fire(self):
        self.game.bullets.add(Bullet(self.game,self.x, self.y-self.halfheight))
        sounds.laser0.play()

    def destroyed(self):
        sounds.spaceshipexplosion.play()
        self.isDead=True
        self.isDeadCount=self.game.count
        self.game.scoreBoard.died()


    def draw(self):
        if not self.isDead:
            super().draw()  

class Container(object):
    """
    handles all collections of objects in the game
    """
    def __init__(self,game):
        self.all={}
        self.dead=[]
        self.game = game

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
    def __init__(self,game):
        super().__init__(game)

class Enemies(Container):
    """
    handles all enemies in the game
    """
    def __init__(self,game):
        super().__init__(game)

    def checkIsHit(self, item):
        isHit=False
        for enemy in self.game.enemies.allItems():
            #print(self.distance_to(enemy))
            if enemy.isHit(item):
                enemy.destroyed()
                isHit=True
        return isHit

class ScoreBoard(object):
    """
    handles all objects in the game
    """
    def __init__(self, game, life=3):
        self.lineY= HEIGHT//20
        self.scoreX = (9.75*WIDTH)//12
        self.lifeX = (2*WIDTH)//4
        self.score=0
        self.life=life
        self.game = game

    def drawMenu(self):
        scoreStr="Score: {0:04d}".format(self.score)
        lifeStr="Life: {0}".format(self.life)
        screen.draw.text(scoreStr, center=(self.scoreX, self.lineY), owidth=0.5, ocolor=(0,0,0), color=(255,255,204) , fontsize=60)
        screen.draw.text(lifeStr, center=(self.lifeX, self.lineY), owidth=0.5, ocolor=(0,0,0), color=(255,255,204) , fontsize=60)

    def update(self):
        pass

    def draw(self):
        self.drawMenu()

    def incScore(self,value=1):
        self.score+=value

    def died(self):
        self.incScore(-1)
        if self.life > 1:
            self.life-=1
        else:
            self.life=0
            self.game.gameOver()


class Game(object):
    """
    handles all objects in the game
    """
    def __init__(self):
        self.background=Background(self)
        self.spaceship=Spaceship(self)
        self.enemies=Enemies(self)
        self.bullets=Bullets(self)
        self.scoreBoard=ScoreBoard(self)
        self.count=0

    def update(self):
        self.background.update()
        self.spaceship.update()
        self.enemies.update()
        self.bullets.update()
        self.scoreBoard.update()
        self.addEnemies()
        self.count+=1
        
    def draw(self):
        self.background.draw()
        self.spaceship.draw()
        self.enemies.draw()
        self.bullets.draw()
        self.scoreBoard.draw()

    def addEnemies(self):
        if self.count % 100 == 0:
            self.enemies.add(EnemyShip(self))

    def gameOver(self):
        global mode
        mode = Mode.GameOver

class GameOver(object):
    """
    handles all objects in the game
    """
    def __init__(self):
        self.background=Background(0)
        #self.count=0

    def drawMenu(self):
        screen.draw.text(TITLE , center=(WIDTH//2, HEIGHT//4), owidth=0.5, ocolor=(0,0,0), color=(255,255,0) , fontsize=100)
        screen.draw.text("GAME OVER" , center=(WIDTH//2, (1.15*HEIGHT)//2), owidth=0.5, ocolor=(255,255,255), color=(255,64,0) , fontsize=70)
        screen.draw.text("press SPACE to start" , center=(WIDTH//2, (7*HEIGHT)//8), owidth=0.5, ocolor=(0,0,0), color=(0,255,0) , fontsize=40)
        game.scoreBoard.draw()

    def controls(self):
        global mode, game
        if keyboard.space:
            mode = Mode.Play
            game = Game() 

    def update(self):
        self.controls()
        self.background.update()
        #self.count+=1
        
    def draw(self):
        self.background.draw()
        self.drawMenu()


game = Game() 
gameOver = GameOver()
#Pygame main loop
# Pygame Zero calls the update and draw functions each frame


# if player.status == 1: screen.draw.text("GAME OVER" , center=(300, 434), owidth=0.5, ocolor=(255,255,255), color=(255,64,0) , fontsize=40)

#we do all of the necessary calcuations in here
def update():
    if mode == Mode.Play:
        game.update()
    else:
        gameOver.update()


#here we redraw everything     
def draw():
    if mode == Mode.Play:
        game.draw()
    else:
        gameOver.draw()

# The mixer allows us to play sounds and music
try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)

    music.play("theme")
    music.set_volume(0.3)

except:
    # If an error occurs (e.g. no sound device), just ignore it
    pass

# Tell Pygame Zero to start - this line is only required when running the game from an IDE such as IDLE or PyCharm
pgzrun.go()
