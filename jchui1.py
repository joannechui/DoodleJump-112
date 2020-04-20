#Joanne Chui
#112 Term Project

#citations
#cmu_112_graphics pkg and animation framework referenced from 
#https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
from cmu_112_graphics import *
import random


def appStarted(app):
    app.gravity = .15
    #circle coordinates
    app.cx = app.width/2
    app.cy = app.height/2
    #circle radius
    app.r = 15
    #velocity in x and y dir
    app.xv = 0
    app.yv = 10
    app.timerDelay = 10
    app.bullets = []
    app.platforms = []
    app.platWidth = 60
    app.platHeight = 10
    initPlatforms(app)
    app.direction = 1
    app.base = 0
    app.movingPlat = []

    app.jumpHeight = app.yv / app.gravity
    app.scrollY = 0
    app.prevPlat = (0, 0)
    app.scrollMargin = app.height - (app.cy + app.jumpHeight)

    app.monsterX = -10
    app.monsterY = -10
    app.possiblePlat = []
    initMonster(app)


def makeDoodlerVisible(app):
    # scroll to make player visible as needed
    if (app.cy < app.scrollY + app.scrollMargin):
        app.scrollY = app.cy - app.scrollMargin
        generatePlatforms(app)
        removePlatforms(app)
    elif (app.cy > app.scrollY + app.height - app.scrollMargin):
        app.scrollY = app.cy - app.height + app.scrollMargin
    

#initialize platforms for the starting screen
def initPlatforms(app):
    #starting platform
    app.currentPlat = [170, app.height - 15, 'green']
    app.platforms.append(app.currentPlat)
    #generate random platforms
    while (len(app.platforms) < 8):
        app.platforms.append([random.randint(0, app.width-40), 
                            random.randint(0, app.height), 'green'])

def generatePlatforms(app):
    app.base = int(app.cy - app.height)
    app.limit = int(app.base + app.scrollMargin)
    newPlatforms = random.randint(1, 4)
    # for i in range(newPlatforms):
    while len(app.platforms) < 20:
        app.platforms.append([random.randint(0, app.width-40), 
                            random.randint(app.base, app.limit), 'green'])
    

def removePlatforms(app):
    i = 0
    while i < len(app.platforms):
        platX, platY = app.platforms[i][0], app.platforms[i][1]
        if (platY >= app.cy + app.height):
            app.platforms.pop(i)
        else:
            i += 1

def selectMovingPlatforms(app):
    while len(app.movingPlat) < 3:
        platIndex = random.randint(0, len(app.platforms) - 1)
        app.movingPlat.append(platIndex)
    movePlatform(app)

def movePlatform(app):
    for i in app.movingPlat:
        if app.platforms[i][1] < app.cy + app.height:
            velocity = random.randint(3, 6)
            app.platforms[i][2] = 'pink'
            app.platforms[i][0] += velocity*app.direction
            if (app.platforms[i][0] + app.platWidth >= app.width or 
                app.platforms[i][0] <= 1):
                app.direction = -app.direction


def timerFired(app):   
    if app.cy < app.monsterY:
        nextPlatX, nextPlatY = moveToBestPlat(app)
        diffX = nextPlatX - app.monsterX
        diffY = nextPlatY - app.monsterY
        app.monsterX += diffX/app.timerDelay 
        app.monsterY += diffY/app.timerDelay
        print('asdf')
        # app.monsterX, app.monsterY = nextPlatX, nextPlatY
    getPlatform(app)
    makeDoodlerVisible(app)
    selectMovingPlatforms(app)

def getDoodleBounds(app):
    x0, y0 = app.cx - app.r, app.cy - app.r
    x1, y1 = app.cx + app.r, app.cy + app.r
    return (x0, y0, x1, y1)

def getPlatformBounds(app, platX, platY):
    x0, y0 = platX, platY
    x1, y1 = platX + app.platWidth, platY + app.platHeight
    return (x0, y0, x1, y1)

#make the character bounce when colliding w/ a platform
def getPlatform(app):
    app.cx += app.xv
    app.cy += app.yv
    app.yv += app.gravity
    doodleBounds = getDoodleBounds(app)
    for i in range(len(app.platforms)):
        platX, platY = app.platforms[i][0], app.platforms[i][1]
        platformBounds = getPlatformBounds(app, platX, platY)
        if (app.yv > 0 and 
            boundsCollide(app, doodleBounds, platformBounds) == True):
            app.prevPlat = app.currentPlat
            app.currentPlat = [platX, platY]
            app.yv = -10
            bounce(app)
            return [platX, platY]

def bounce(app):
    app.yv += app.gravity

def boundsCollide(app, bound1, bound2):
    (ax0, ay0, ax1, ay1) = bound1
    (bx0, by0, bx1, by1) = bound2
    return ((ax1 >= bx0) and (bx1 >= ax0) and
            (ay1 >= by0) and (by1 >= ay0))

def newPlatformCollide(app, x, y):
    plat = getPlatform(app)
    if plat != app.currentPlat:
        app.currentPlat = plat
        return True
    return False

def moveDoodler(app, dx):
    app.cx -= dx
    #wraparound
    if (app.cx + app.r <= 0):
            app.cx = app.width - app.r
    elif (app.cx - app.r >= app.width):
            app.cx = app.r

def keyPressed(app, event):
    if (event.key == 'Left'):
        moveDoodler(app, 10)
    elif (event.key == 'Right'):
        moveDoodler(app, -10)
    elif (event.key == 'Up'):
        shoot(app)

def initMonster(app):
    app.monsterX, app.monsterY = getRandomPlat(app)

def getRandomPlat(app):
    index = random.randint(0, len(app.platforms)-1)
    startX, startY = app.platforms[index][0], app.platforms[index][1]
    return (startX, startY)

def monsterJump(app):
    for i in range(len(app.platforms)):
        platX, platY = app.platforms[i][0], app.platforms[i][1]
        dist = getDistanceBetweenPlat(app, platX, platY, 
                                        app.monsterX, app.monsterY)
        if (platY < app.monsterY and dist <= app.jumpHeight):
            app.monsterX, app.monsterY = platX, platY

def moveToBestPlat(app):
    app.possiblePlat = []
    platX, platY = app.currentPlat[0], app.currentPlat[1]
    if possibleJump(app, app.monsterX, app.monsterY,platX, platY):
        app.monsterX, app.monsterY = platX, platY
    i = 0
    print('platforms', app.platforms)
    for i in range(len(app.platforms)):
        platX1, platY1 = app.platforms[i][0], app.platforms[i][1]
        if possibleJump(app, app.monsterX, app.monsterY, platX1, platY1):
            app.possiblePlat.append(app.platforms[i])
    print('possibleplatforms', app.possiblePlat)
    bestPlat = getBestPlat(app)
    print('bestPlat', bestPlat)
    return bestPlat[0], bestPlat[1]


#if distance within jumpheight, return true
def possibleJump(app, x0, y0, x1, y1):
    yLimit = app.height // 2
    xLimit = app.width // 2 
    if y1 >= y0 or y1 < app.currentPlat[1]:
        return False
    elif (abs(y0 - y1 )<= yLimit) and (abs(x0 - x1) <= xLimit):
        return True
    else: 
        return False

def getBestPlat(app):
    i = 0
    bestDist = 0
    bestPlat = [app.monsterX, app.monsterY]
    for i in range(len(app.possiblePlat)):
        platX, platY = app.possiblePlat[i][0], app.possiblePlat[i][1]
        currDist = ((platX - app.monsterX)**2 + (platY - app.monsterY)**2)**.5
        if (currDist > bestDist):
            bestDist = currDist
            bestPlat = [platX, platY]
    return bestPlat


#shoot bullets feature
def shoot(app):
    app.bullets.append((app.cx, app.cy))
    index = 0
    while (index < len(app.bullets)):
        x, y = app.bullets[index]
        if (y > 0):
            app.bullets.pop(index)
            y -= 10
            app.bullets.append((x, y))
        else:
            index += 1

def drawMonster(app, canvas):
    x = app.monsterX
    y = app.monsterY - app.scrollY
    canvas.create_oval(x - app.r, y - app.r,
                        x + app.r, y + app.r, 
                        fill = 'red')
        
def drawBullet(app, canvas):
    r = 5
    for (x, y) in app.bullets:
        canvas.create_oval(x, y, x+r, y+r, fill = 'red')


def drawPlatform(app, canvas):
    for i in range(len(app.platforms)):
        platX, platY = app.platforms[i][0], app.platforms[i][1]
        color = app.platforms[i][2]
        platY -= app.scrollY
        platRight = platX + app.platWidth
        platBottom = platY + app.platHeight
        canvas.create_rectangle(platX, platY, 
                            platRight, platBottom, 
                            fill = color)
                            

def redrawAll(app, canvas):
    y = app.cy
    y -= app.scrollY
    canvas.create_oval(app.cx - app.r, y - app.r,
                        app.cx + app.r, y + app.r, 
                        fill = 'blue')
    drawMonster(app, canvas)
    drawPlatform(app, canvas)
    # drawMovingPlat(app, canvas)
    drawBullet(app, canvas)


runApp(width=400, height=600)

