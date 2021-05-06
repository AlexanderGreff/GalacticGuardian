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

class Mode(Enum):
    GameOver = 1
    Play = 2

# Set up constants
WIDTH = 720
HEIGHT = 720
TITLE = "Galactic Guardian"

#globals
mode = Mode.GameOver
players=None
gameOver=None
class Background(object):
    """
    handles logic for scrolling background
    """
    def __init__(self, scrollSpeed=5):
        """
        constructor
        """
        self.MAX_IMAGE_Y = 1044
        self.PIXEL_SCROLL = scrollSpeed
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
    handles logic for an enemy ship
    """
    AllShips=["enemyblue2","enemyship5","enemyship4","enemyship3","enemyship1"]
    NbPointFactor=5

    def __init__(self,game):
        randval = random.randrange(1, len(EnemyShip.AllShips) + 1)
        super().__init__(EnemyShip.AllShips[randval-1])  
        self.shipKind = randval
        self.x = random.randrange(0, WIDTH)
        self.y =  20
        self.shipspeed=5
        self.halfheight=self.height/2
        self.movex=0
        self.movey=0
        self.game = game

    @staticmethod
    def drawAllShips(y):
        sideSpace=100
        spaceForShips=WIDTH-2*sideSpace
        numberShips=len(EnemyShip.AllShips)
        for i in range(numberShips):
            x=sideSpace-30+(spaceForShips/(numberShips-1))*i
            screen.blit(EnemyShip.AllShips[i], (x,y))
            nbPoints=(i+1)*EnemyShip.NbPointFactor
            screen.draw.text(str(nbPoints) , center=(x+30, y+100), owidth=0.5, ocolor=(0,0,0), color=(0,255,0) , fontsize=40)



    def nbPoints(self):
        return self.shipKind * EnemyShip.NbPointFactor

    def controls(self):
        if (self.game.count % 10 == 0):
            xmin = random.randrange(2, 9 + self.shipKind)
            self.movex = random.randrange(-xmin, xmin)
            self.movey = random.randrange(0,2 + self.shipKind)
        return self.movex, self.movey

    def isHit(self, item):
        return self.colliderect(item)

    def destroyed(self,incScore): 
        if incScore:
            self.game.scoreBoard.incScore(self.nbPoints())
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
            sounds.enemy_escaped.play()
            self.game.scoreBoard.incScore(-self.nbPoints())
            self.game.enemies.remove(self)

class Bullet(Actor):
    """
    handles logic for a bullet
    """
    def __init__(self,game,x,y):
        super().__init__("bullet15")
        self.x = x
        self.y = y
        self.speed=5
        self.game = game

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
    handles logic for the player spaceship
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
        self.game = game

    def controls(self):
        movex = 0
        movey = 0
        if not self.isDead:
            if keyboard.s or keyboard.down:
                movey = self.shipspeed
                sounds.engineshorter.play()
            elif keyboard.w or keyboard.up:
                movey = -self.shipspeed
                sounds.engineshorter.play()

            if keyboard.space:
                if self.countFire % 10 == 0:
                    self.fire()
                self.countFire+=1

            if keyboard.a or keyboard.left:
                movex = -self.shipspeed
                # sounds.engineshorter.play()
            elif keyboard.d or keyboard.right:
                movex = self.shipspeed
                # sounds.engineshorter.play()
            if keyboard.q:
                self.game.quit()
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
        if not self.isDead and self.game.enemies.checkIsHit(self,incScore=False):
            self.destroyed()

    def fire(self):
        self.game.bullets.add(Bullet(self.game,self.x, self.y-self.halfheight))
        sounds.laser0.play()

    def destroyed(self):
        sounds.spaceshipexplosion.play()
        self.isDead=True
        self.isDeadCount=self.game.count
        self.game.died()


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
    handles all bullets of a player
    """
    def __init__(self,game):
        super().__init__(game)

class Enemies(Container):
    """
    handles all enemies of a player
    """
    def __init__(self,game):
        super().__init__(game)

    def checkIsHit(self, item, incScore=True):
        isHit=False
        for enemy in self.game.enemies.allItems():
            #print(self.distance_to(enemy))
            if enemy.isHit(item):
                enemy.destroyed(incScore)
                isHit=True
        return isHit

class ScoreBoard(object):
    """
    handles the scoreboard of a player
    """
    def __init__(self, game, life=3):
        self.lineY1= (1*HEIGHT)//20
        self.lineY2= (2*HEIGHT)//20
        self.scoreX = (9.65*WIDTH)//12
        self.lifeX = (2*WIDTH)//4
        self.playerX = (1*WIDTH)//8
        self.score=0
        self.life=life
        self.game = game

    def drawBoard(self,player,alwaysLine1):
        if alwaysLine1:
            lineY=self.lineY1
        elif player==0:
            lineY=self.lineY1
        else:
            lineY=self.lineY2
        
        scoreStr="Score: {0:05d}".format(self.score)
        lifeStr="Life: {0}".format(self.life)
        playerStr="Player: {0}".format(player+1)
        screen.draw.text(scoreStr, center=(self.scoreX,lineY), owidth=0.5, ocolor=(0,0,0), color=(255,255,204) , fontsize=60)
        if self.life >0:
            screen.draw.text(lifeStr, center=(self.lifeX,lineY), owidth=0.5, ocolor=(0,0,0), color=(255,255,204) , fontsize=60)
        screen.draw.text(playerStr, center=(self.playerX,lineY), owidth=0.5, ocolor=(0,0,0), color=(255,255,204) , fontsize=60)

    def update(self):
        pass

    def draw(self):
        self.drawBoard(self.game.playerNb,True)

    def incScore(self,value=1):
        self.score+=value
        if self.score < 0:
            self.score=0

    def died(self):
        if self.life > 1:
            self.life-=1
        else:
            self.life=0
            players.gameOver()


class Game(object):
    """
    handles all states for the Game of 1 player
    """
    def __init__(self,players,playerNb):
        self.background=Background()
        self.spaceship=Spaceship(self)
        self.enemies=Enemies(self)
        self.bullets=Bullets(self)
        self.scoreBoard=ScoreBoard(self)
        self.count=0
        self.playerNb=playerNb
        self.players=players

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

    def died(self):
        self.scoreBoard.died()
        self.players.died()

    @staticmethod
    def quit():
         pygame.display.quit()
         pygame.quit()
         sys.exit()
        
class GameOver(object):
    """
    handles Game Over state
    """
    def __init__(self):
        self.background=Background(3)

    def drawMenu(self):
        screen.draw.text(TITLE , center=(WIDTH//2, HEIGHT//4), owidth=0.5, ocolor=(0,0,0), color=(255,255,0) , fontsize=100)
        EnemyShip.drawAllShips((1.2*HEIGHT)//4+20)
        screen.blit("spaceshipsmall", (WIDTH//2-30, HEIGHT//1.9))
        screen.draw.text("GAME OVER" , center=(WIDTH//2, (2.15*HEIGHT)//3), owidth=0.5, ocolor=(255,255,255), color=(255,64,0) , fontsize=90)
        screen.draw.text("A Game Made By Alexander Greff" , center=(WIDTH//2, (7.2*HEIGHT)//9), owidth=0.5, ocolor=(0,0,0), color=(140,112,219) , fontsize=40)
        screen.draw.text("Press 1 or 2 for number of players" , center=(WIDTH//2, (7.9*HEIGHT)//9), owidth=0.5, ocolor=(0,0,0), color=(0,255,0) , fontsize=40)
        screen.draw.text(" q to quit" , center=(WIDTH//2, (8.3*HEIGHT)//9), owidth=0.5, ocolor=(0,0,0), color=(0,255,0) , fontsize=40)
        if players is not None:
            players.drawBoard()

    def controls(self):
        global mode, players
        if keyboard.K_1:
            mode = Mode.Play
            players = Players(1) 
        elif keyboard.K_2:
            mode = Mode.Play
            players = Players(2)
        elif keyboard.q:
                Game.quit()

    def update(self):
        self.controls()
        self.background.update()
        
    def draw(self):
        self.background.draw()
        self.drawMenu()

class Players(object):
    """
    handles all players in the game
    """
    def __init__(self,numberPlayers):
        self.numberPlayers=numberPlayers
        self.currentPlayer=0
        self.players=[]
        for i in range(numberPlayers):
            self.players.append(Game(self,i))
        self.countPlayerChange=0

    def getPlayer(self):
        return self.players[self.currentPlayer]

    def update(self):
        if not self.playerChange():
            self.getPlayer().update()   

    def drawBoard(self):
        for i in range(self.numberPlayers):
            self.players[i].scoreBoard.drawBoard(i,False)

    def draw(self):
        if not self.playerChange():
            self.getPlayer().draw()
        else:
            self.drawSplash()

    def drawSplash(self):
        screen.draw.filled_rect(Rect((0, 0), (WIDTH, HEIGHT)), (0, 0, 0))
        playerStr="Player {0}".format(self.currentPlayer+1)
        screen.draw.text(playerStr, center=(WIDTH//2,HEIGHT//2), owidth=0.5, ocolor=(0,0,0), color=(255,255,0) , fontsize=120)
        screen.draw.text("Press SPACE to skip" , center=(WIDTH//2, (7*HEIGHT)//8), owidth=0.5, ocolor=(0,0,0), color=(255,0,0) , fontsize=40)
        if keyboard.space: # done changing player
            self.countPlayerChange=0

    def nextPlayer(self):
        currentPlayer = self.currentPlayer
        self.currentPlayer+=1
        if self.currentPlayer == self.numberPlayers:
            self.currentPlayer=0
        if currentPlayer != self.currentPlayer:
            self.countPlayerChange=1
    
    def died(self):
        self.nextPlayer()

    def playerChange(self):
        changing = self.countPlayerChange > 0 and self.countPlayerChange < 500
        if changing:
            self.countPlayerChange+=1
        else:
            self.countPlayerChange=0
        return changing

    def gameOver(self):
        global mode
        if self.currentPlayer == (self.numberPlayers-1):
            mode = Mode.GameOver

#initalize global
gameOver = GameOver()

#Pygame main loop
# Pygame Zero calls the update and draw functions each frame

#we do all of the necessary calcuations in here
def update():
    if mode == Mode.Play:
        players.update()
    else:
        gameOver.update()

#here we redraw everything     
def draw():
    if mode == Mode.Play:
        players.draw()
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
