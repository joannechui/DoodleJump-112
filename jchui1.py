#Joanne Chui
#112 Term Project

#citations
#cmu_112_graphics pkg and animation framework referenced from 
#https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
#sidescrolling framework and subclassing modalmode/mode referenced from
#https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
from cmu_112_graphics import *
import random
import copy
import math

class SplashScreenMode(Mode):
    #rgbString taken from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
    def rgbString(mode, red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)
    
    def drawGrid(mode, canvas):
        gridDim = 10
        rows = mode.height // gridDim
        cols = mode.width // gridDim
        peach = mode.rgbString(240, 200, 175)
        for i in range(rows):
            canvas.create_line(0, i*gridDim, mode.width, i*gridDim, fill = peach, width = 1)
        for j in range(cols):
            canvas.create_line(j*gridDim, 0, j*gridDim, mode.height, fill = peach, width = 1)

    def redrawAll(mode, canvas):
        tan = mode.rgbString(250, 240, 230)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = tan)
        mode.drawGrid(canvas)
        font = 'Arial 16'
        canvas.create_text(mode.width/2, 200, text = 'doodle jump', font = 'Arial 30')
        canvas.create_text(mode.width/2, 300, text = 'press "s" to start', font = font)
        canvas.create_text(mode.width/2, 350, text = 'press "i" for instructions', font = font)
    def keyPressed(mode, event):
        if (event.key == 'i' or event.key == 'I'):
            mode.app.setActiveMode(mode.app.instructionMode)
        elif (event.key == 's' or event.key == 'S'):
            mode.app.setActiveMode(mode.app.gameMode)

class GameMode(Mode):
    def appStarted(mode):
        print('appStarted')
        mode.gravity = .15
        #circle coordinates
        mode.cx = mode.width/2
        mode.cy = mode.height/2
        #circle radius
        mode.r = 15
        #velocity in x and y dir
        mode.xv = 0
        mode.yv = 8
        mode.time = 10
        mode.monsterTime = 0
        mode.platforms = []
        mode.platWidth = 60
        mode.platHeight = 10
        mode.initPlatforms()
        mode.direction = 1
        mode.base = 0
        mode.movingPlat = []
        mode.rotatePlatIndex = []
        mode.rotatePlat = []
        mode.theta = 90

        mode.jumpHeight = mode.yv / mode.gravity
        mode.scrollY = 0
        mode.prevPlat = (0, 0)
        mode.scrollMargin = mode.height - (mode.cy + mode.jumpHeight)

        mode.monsterX = -100
        mode.monsterY = 0
        mode.monsterXVel = 0
        mode.possiblePlat = []
        mode.possiblePlatIndex = []
        mode.bestPlatIndex = -1

        mode.bullets = []
        mode.bulletXV = 0
        mode.bulletYV = 10

        mode.springX = -10
        mode.springY = -10
        mode.springDim = 7
        mode.randPlatCol = 'green'

        mode.score = 0


    def makeDoodlerVisible(mode):
        print('makeDoodlerVisible')
        # scroll to make player visible as needed
        if (mode.cy < mode.scrollY + mode.scrollMargin):
            mode.scrollY = mode.cy - mode.scrollMargin
            mode.generatePlatforms()
            mode.removePlatforms()
            mode.removeRotatePlatform()
            mode.removeBullet()
        elif (mode.cy > mode.scrollY + mode.height - mode.scrollMargin):
            mode.scrollY = mode.cy - mode.height + mode.scrollMargin
        

    #initialize platforms for the starting screen
    def initPlatforms(mode):
        print('initPlatforms')
        #starting platform
        mode.currentPlat = [170, mode.height - 15, 'green']
        mode.platforms.append(mode.currentPlat)
        numPlatforms = random.randint(10, 14)
        #generate random platforms
        mode.platY, mode.platX = mode.currentPlat[1], mode.currentPlat[0]
        while len(mode.platforms) < numPlatforms:
            platY = random.randint(0, mode.height-15)
            platX = random.randint(0, mode.width-40)
            if (mode.platY - platY >= 30 and 
                    mode.platY - platY <= 60 and
                    abs(mode.platX - platX) < 150):
                mode.platY = platY
                mode.platX = platX
                mode.platforms.append([mode.platX, mode.platY, 'green'])
            

    def generatePlatforms(mode):
        print('generatePlatforms')
        mode.base = int(mode.platY - mode.height)
        mode.limit = int(mode.platY + mode.scrollMargin)
        if len(mode.platforms) < 25:
            platY = random.randint(mode.base, mode.limit)
            platX = random.randint(0, mode.width-40)
            while (mode.platY - platY < 40 or 
                    mode.platY - platY > 70 or
                    abs(mode.platX - platX) > 200):
                platY = random.randint(mode.base, mode.limit)
                platX = random.randint(0, mode.width-40)
            mode.platY = platY
            mode.platX = platX
            mode.platforms.append([mode.platX, mode.platY, 'green'])
        

    def removePlatforms(mode):
        print('removePlatforms')
        i = 0
        while i < len(mode.platforms):
            platX, platY = mode.platforms[i][0], mode.platforms[i][1]
            if (platY >= mode.cy + mode.height):
                mode.platforms.pop(i)
                if mode.bestPlatIndex != None:
                    mode.bestPlatIndex -= 1
                j = 0
                while j < len(mode.movingPlat):
                    if (mode.movingPlat[j] < 0):
                        mode.movingPlat.pop(j)
                    else:
                        mode.movingPlat[j] -= 1
                        j += 1
                k = 0
                while k < len(mode.rotatePlatIndex):
                    if (mode.rotatePlatIndex[k] < 0):
                        mode.rotatePlatIndex.pop(k)
                    else:
                        mode.rotatePlatIndex[k] -= 1
                        k += 1
            else:
                i += 1


    def selectRotatePlatforms(mode):
        print('selectRotatePlatforms')
        if len(mode.rotatePlatIndex) < 15:
            i = random.randint(1, len(mode.platforms)-1)
            if (i not in mode.movingPlat and 
                i not in mode.rotatePlatIndex and
                mode.platforms[i][1] < mode.currentPlat[1] - mode.jumpHeight*2 and
                mode.legalRotatePlatform(i)):
                mode.rotatePlatIndex.append(i)
        mode.rotatePlatform()

    def legalRotatePlatform(mode, index):
        if index > len(mode.platforms) - 2:
            return False
        if (mode.platforms[index][1] - mode.platforms[index + 1][1] > 60 and
            mode.platforms[index - 1][1] - mode.platforms[index][1] > 60):
            return True
        else:
            return False

    def rotatePlatform(mode):
        print('rotatePlatform')
        index = 0
        for i in mode.rotatePlatIndex:
            mode.rotateCX, mode.rotateCY = mode.platforms[i][0], mode.platforms[i][1]
            mode.platforms[i][2] = 'black'
            mode.lineX, mode.lineY = mode.rotateCX + mode.platWidth, mode.rotateCY
            if len(mode.rotatePlat) < len(mode.rotatePlatIndex):
                mode.rotatePlat.append([mode.rotateCX, mode.rotateCY, mode.lineX, mode.lineY])
            else:
                mode.rotatePlat[index] = [mode.rotateCX, mode.rotateCY, mode.lineX, mode.lineY]
                index += 1
            mode.getTheta()

    def getTheta(mode):
        print('getTheta')
        mode.theta -= .5
        if mode.theta < -360:
            mode.theta += 360
        mode.rotateCoord()

    def rotateCoord(mode):
        print('rotateCoord')
        for i in range(len(mode.rotatePlat)):
            mode.rotateX = mode.platWidth * math.sin(math.radians(mode.theta))
            mode.rotateY = mode.platWidth * math.sin(math.radians(90 - mode.theta))
            mode.rotatePlat[i][2] = mode.rotateX + mode.rotatePlat[i][0]
            mode.rotatePlat[i][3] = mode.rotateY + mode.rotatePlat[i][1]

    def removeRotatePlatform(mode):
        print('removeRotatePlatform')
        i = 0
        while i < len(mode.rotatePlat):
            platY = mode.rotatePlat[i][1]
            if (platY >= mode.cy + mode.height):
                mode.rotatePlat.pop(i)
            else:
                i += 1

    def selectMovingPlatforms(mode):
        print('selectMovingPlatforms')
        if len(mode.movingPlat) < 3:
            platIndex = random.randint(0, len(mode.platforms) - 1) 
            if (platIndex not in mode.rotatePlatIndex and 
                mode.platforms[platIndex][1] < mode.currentPlat[1] - mode.jumpHeight*2): 
                mode.movingPlat.append(platIndex)
        mode.movePlatform()

    def movePlatform(mode):
        print('movePlatform')
        for i in range(len(mode.platforms)):
            mode.platforms[i][2] = 'green'
        for i in mode.movingPlat:
            velocity = 2 #random.randint(1, 3)
            mode.platforms[i][2] = 'pink'
            mode.platforms[i].append(1) #for direction
            mode.platforms[i][0] += velocity*mode.platforms[i][3]
            if (mode.platforms[i][0] + mode.platWidth >= mode.width or 
                mode.platforms[i][0] <= 1):
                mode.platforms[i][3] = -mode.platforms[i][3]

    def keepScore(mode):
        if mode.yv < 0:
            if mode.score < abs(int(mode.cy)):
                mode.score = abs(int(mode.cy))

    def timerFired(mode):
        mode.keepScore()
        mode.getPlatform()
        mode.getRotatePlatform()
        mode.makeDoodlerVisible()
        mode.selectMovingPlatforms()
        mode.selectRotatePlatforms()
        mode.springPowerUp()
        mode.shoot()
        mode.bulletHit()
        mode.monsterHit()
        mode.doodleFall()
        mode.monsterTime += mode.time
        if (mode.monsterY > mode.cy + mode.height and 
            mode.monsterTime % 300 == 0):
            mode.initMonster()

        if (mode.cy < mode.monsterY and mode.monsterTime % 300 == 0):
            mode.bestPlatIndex = mode.monsterJump()
            if mode.bestPlatIndex != -1 and mode.bestPlatIndex != None:
                mode.monsterX = mode.platforms[mode.bestPlatIndex][0]
                mode.monsterY = mode.platforms[mode.bestPlatIndex][1]
                if mode.bestPlatIndex in mode.movingPlat:
                    mode.monsterXVel = mode.platforms[mode.bestPlatIndex][3]
                else:
                    mode.monsterXVel = 0

        mode.monsterX += mode.monsterXVel*2
        if (mode.monsterX + mode.platWidth >= mode.width or 
                mode.monsterX <= 0):
                mode.monsterXVel = -mode.monsterXVel

    def doodleFall(mode):
        print('doodleFall')
        if mode.cy > mode.platforms[0][1] + mode.height/2:
            mode.appStarted()
            mode.app.setActiveMode(mode.app.gameOverMode)

    def getDoodleBounds(mode):
        print('getDoodleBounds')
        x0, y0 = mode.cx - mode.r, mode.cy - mode.r
        x1, y1 = mode.cx + mode.r, mode.cy + mode.r
        return (x0, y0, x1, y1)

    def getPlatformBounds(mode, platX, platY):
        print('getPlatformBounds')
        x0, y0 = platX, platY
        x1, y1 = platX + mode.platWidth, platY + mode.platHeight
        return (x0, y0, x1, y1)

    #check if player hits rotating platform
    def getRotatePlatformBounds(mode, x0, y0, x1, y1):
        print('getRotatePlatformBounds')
        if (x1 - x0 != 0):
            m = (y1 - y0) / (x1 - x0)
        else:
            m = 1
        b = y1 - m*x1
        doodleX0, doodleY0, doodleX1, doodleY1 = mode.getDoodleBounds()
        diff = abs(doodleY1 - (m*mode.cx + b))
        if mode.yv > 0 and diff < 2:
            mode.prevPlat = mode.currentPlat
            mode.currentPlat = [x0, y0]
            angle = 0
            mode.yv = -8
            if mode.theta % -90 != 0:
                angle = mode.theta % -90
                if ((mode.theta > -90) or
                    (mode.theta < -180 and mode.theta > -270)):
                    mode.xv = angle*.03
                else:
                    mode.xv = -angle*.03
            mode.bounce()

    def getRotatePlatform(mode):
        print('getRotatePlatform')
        for i in range(len(mode.rotatePlat)):
            x0, y0 = mode.rotatePlat[i][0], mode.rotatePlat[i][1]
            x1, y1 = mode.rotatePlat[i][2], mode.rotatePlat[i][3]
            mode.getRotatePlatformBounds(x0, y0, x1, y1)

    def boundsCollide(mode, bound1, bound2):
        print('bpundsCollide')
        (ax0, ay0, ax1, ay1) = bound1
        (bx0, by0, bx1, by1) = bound2
        print(((ax1 >= bx0) and (bx1 >= ax0) and
                (ay1 >= by0) and (by1 >= ay0)))
        return ((ax1 >= bx0) and (bx1 >= ax0) and
                (ay1 >= by0) and (by1 >= ay0))


    #make the character bounce when colliding w/ a platform
    def getPlatform(mode):
        print('getPlatform')
        mode.cx += mode.xv
        mode.cy += mode.yv
        mode.yv += mode.gravity
        doodleBounds = mode.getDoodleBounds()
        for i in range(len(mode.platforms)):
            if i not in mode.rotatePlatIndex:
                platX, platY = mode.platforms[i][0], mode.platforms[i][1]
                platformBounds = mode.getPlatformBounds(platX, platY)
                if (mode.yv > 0 and 
                    mode.boundsCollide(doodleBounds, platformBounds) == True):
                    mode.prevPlat = mode.currentPlat
                    mode.currentPlat = [platX, platY]
                    mode.yv = -8
                    mode.xv = 0
                    mode.bounce()
                    return [platX, platY]

    def bounce(mode):
        # print('bounce')
        mode.yv += mode.gravity

    def moveDoodler(mode, dx):
        mode.cx -= dx
        #wraparound
        if (mode.cx + mode.r <= 0):
                mode.cx = mode.width - mode.r
        elif (mode.cx - mode.r >= mode.width):
                mode.cx = mode.r

    def keyPressed(mode, event):
        if (event.key == 'Left'):
            mode.moveDoodler(5)
        elif (event.key == 'Right'):
            mode.moveDoodler(-5)
        elif (event.key == 'Up'):
            mode.bulletYV = -10
            mode.bullets.append([mode.cx, mode.cy, 0, mode.bulletYV])
        elif (event.key == 'Down'):
            mode.bulletYV = 10
            mode.bullets.append([mode.cx, mode.cy, 0, mode.bulletYV])
        elif (event.key == 'a' or event.key == 'A'):
            if (mode.bulletXV > -20):
                mode.bulletXV -= 3
            mode.bullets.append([mode.cx, mode.cy, mode.bulletXV, mode.bulletYV])
        elif (event.key == 'd' or event.key == 'D'):
            if (mode.bulletXV < 20):
                mode.bulletXV += 3
            mode.bullets.append([mode.cx, mode.cy, mode.bulletXV, mode.bulletYV])
        elif (event.key == 'i' or event.key == 'I'):
            mode.app.setActiveMode(mode.app.instructionMode)

    def springPowerUp(mode):
        print('springPowerUp')
        if mode.springY > mode.currentPlat[1] + mode.height/2:
            i = random.randint(0, len(mode.platforms)-1)
            if (i not in mode.movingPlat and 
                i not in mode.rotatePlatIndex and 
                mode.platforms[i][1] < mode.currentPlat[1] - mode.height/2):
                mode.springX, mode.springY = mode.platforms[i][0], mode.platforms[i][1]
            # x, y = mode.getRandomPlat()
            # if (y < mode.currentPlat[1] - mode.height/2 and mode.randPlatCol == 'green'):
            #     mode.springX, mode.springY = x, y
            #     print(mode.springX, mode.springY)
        doodleBounds = mode.getDoodleBounds()
        springBounds = (mode.springX, mode.springY - mode.springDim, 
                        mode.springX + mode.springDim, mode.springY - mode.springDim)
        if mode.boundsCollide(springBounds, doodleBounds) and mode.yv > 0: 
            mode.yv = -12
            mode.bounce()

    def initMonster(mode):
        i = random.randint(0, len(mode.platforms)-1)
        if (i not in mode.movingPlat and 
                i not in mode.rotatePlatIndex and 
                mode.platforms[i][1] < mode.currentPlat[1] - mode.height/2):
                mode.monsterX, mode.monsterY = mode.platforms[i][0], mode.platforms[i][1]


    def getRandomPlat(mode):
        print('getRandomPlat')
        index = random.randint(0, len(mode.platforms)-1)
        startX, startY = mode.platforms[index][0], mode.platforms[index][1]
        mode.randPlatCol = index
        return (startX, startY)

    #change timing so it jumps regularly
    def monsterJump(mode):
        print('monsterJump')
        mode.possiblePlat = []
        mode.possiblePlatIndex = []
        platX, platY = mode.currentPlat[0], mode.currentPlat[1]
        if mode.possibleJump(mode.monsterX, mode.monsterY,platX, platY):
            mode.monsterX, mode.monsterY = platX, platY
        i = 0
        for i in range(len(mode.platforms)):
            platX1, platY1 = mode.platforms[i][0], mode.platforms[i][1]
            if (mode.possibleJump(mode.monsterX, mode.monsterY, platX1, platY1) and
                i not in mode.rotatePlatIndex):
                mode.possiblePlatIndex.append(i)
                # if len(mode.platforms[i]) > 3:
                #     mode.possiblePlat.append([mode.platforms[i][0], mode.platforms[i][1], mode.platforms[i][3]])
                # else:
                #     mode.possiblePlat.append([mode.platforms[i][0], mode.platforms[i][1]])
        bestPlatIndex = mode.getBestPlat()
        if bestPlatIndex != None:
            return bestPlatIndex
            # mode.monsterX = mode.platforms[bestPlatIndex][0]
            # mode.monsterY = mode.platforms[bestPlatIndex][1]
            # if len(mode.platforms[bestPlatIndex]) > 3:
            #     mode.monsterXVel = mode.platforms[bestPlatIndex][3]
            # else:
            #     mode.monsterXVel = 0


    #if distance within x and y bounds, return true
    def possibleJump(mode, x0, y0, x1, y1):
        print('possibleJump')
        yLimit = 100
        xLimit = mode.width // 2 
        if y1 >= y0 or y1 < mode.currentPlat[1]:
            return False
        elif (abs(y0 - y1 )<= yLimit) and (abs(x0 - x1) <= xLimit):
            return True
        else: 
            return False

    def getBestPlat(mode):
        print('getBestPlat')
        i = 0
        bestDist = 0
        bestPlat = None
        for i in mode.possiblePlatIndex:
            platX, platY = mode.platforms[i][0], mode.platforms[i][1]
            currDist = ((platX - mode.monsterX)**2 + (platY - mode.monsterY)**2)**.5
            if (currDist > bestDist):
                bestDist = currDist
                bestPlat = i
        return bestPlat

    # def getBestPlat(mode):
    #     print('getBestPlat')
    #     i = 0
    #     bestDist = 0
    #     bestPlat = [mode.monsterX, mode.monsterY]
    #     for i in range(len(mode.possiblePlat)):
    #         platX, platY = mode.possiblePlat[i][0], mode.possiblePlat[i][1]
    #         currDist = ((platX - mode.monsterX)**2 + (platY - mode.monsterY)**2)**.5
    #         if (currDist > bestDist):
    #             bestDist = currDist
    #             bestPlat = [platX, platY]
    #             if len(mode.possiblePlat[i]) > 2:
    #                 mode.monsterXVel = mode.possiblePlat[i][2]
    #             else:
    #                 mode.monsterXVel = 0
    #     return bestPlat


    #shoot bullets feature
    def shoot(mode):
        print('shoot')
        for i in range(len(mode.bullets)):
            mode.bullets[i][0] += mode.bullets[i][2]
            mode.bullets[i][1] += mode.bullets[i][3]
        mode.bulletBounce()

    def bulletBounce(mode):
        print('bulletBounce')
        for i in range(len(mode.bullets)):
            if (mode.bullets[i][0] >= mode.width or
                mode.bullets[i][0] <= 0):
                mode.bullets[i][2] = -mode.bullets[i][2]

    def removeBullet(mode):
        print('removeBullet')
        i = 0
        while i < len(mode.bullets):
            if mode.bullets[i][1] < mode.base:
                mode.bullets.pop(i)
            else:
                i += 1

    def bulletHit(mode):
        print('bulletHit')
        monsterBounds = (mode.monsterX - mode.r + mode.platWidth/2, 
                            mode.monsterY - mode.r*2,
                            mode.monsterX + mode.r + mode.platWidth/2, 
                            mode.monsterY)
        #kill monster when shot
        for i in range(len(mode.bullets)):
            x, y = mode.bullets[i][0], mode.bullets[i][1]
            bulletBounds = (x-5, y-5, x+5, y+5)
            if mode.boundsCollide(bulletBounds, monsterBounds):
                mode.monsterX = -100
            #delay monster regeneration
            if (mode.monsterX == -100 and mode.monsterTime % 3000 == 0):
                index = random.randint(15, len(mode.platforms)-1)
                mode.monsterX = mode.platforms[index][0]
                mode.monsterY = mode.platforms[index][1]

    def monsterHit(mode):
        print('monsterHit')
        monsterBounds = (mode.monsterX - mode.r + mode.platWidth/2, 
                            mode.monsterY - mode.r*2,
                            mode.monsterX + mode.r + mode.platWidth/2, 
                            mode.monsterY)
        #kill player when monster collides with it
        doodleBounds = mode.getDoodleBounds()
        if mode.boundsCollide(doodleBounds, monsterBounds):
            print('abc')
            mode.appStarted()
            mode.app.setActiveMode(mode.app.gameOverMode)
                

    def drawMonster(mode, canvas):
        x = mode.monsterX
        y = mode.monsterY - mode.scrollY
        canvas.create_oval(x - mode.r + mode.platWidth/2, y - (mode.r*2),
                            x + mode.r + mode.platWidth/2, y, 
                            fill = 'red')
            
    def drawBullet(mode, canvas):
        r = 5
        for i in range(len(mode.bullets)):
            x, y = mode.bullets[i][0], mode.bullets[i][1]
            y -= mode.scrollY
            canvas.create_oval(x, y, x+r, y+r, fill = 'red')


    def drawPlatform(mode, canvas):
        for i in range(len(mode.platforms)):
            if i not in mode.rotatePlatIndex:
                platX, platY = mode.platforms[i][0], mode.platforms[i][1]
                color = mode.platforms[i][2]
                platY -= mode.scrollY
                platRight = platX + mode.platWidth
                platBottom = platY + mode.platHeight
                canvas.create_rectangle(platX, platY,
                                    platRight, platBottom, 
                                    fill = color)

    def drawRotatePlatform(mode, canvas):      
        for i in range(len(mode.rotatePlat)):
            centerX, centerY = mode.rotatePlat[i][0], mode.rotatePlat[i][1]
            endX, endY = mode.rotatePlat[i][2], mode.rotatePlat[i][3]
            centerY -= mode.scrollY
            endY -= mode.scrollY
            canvas.create_line(centerX, centerY, endX, endY, 
                                fill = 'black', width = mode.platHeight)
    
    def drawSpringPowerUp(mode, canvas):
        x, y = mode.springX, mode.springY - mode.springDim
        y -= mode.scrollY
        canvas.create_rectangle(x, y, x + mode.springDim, y + 2*mode.springDim, 
                                fill = 'orange')
    
    def drawScore(mode, canvas):
        canvas.create_text(40, 15, text=f'score: {mode.score}', font='Arial 14')
    
    def rgbString(mode, red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)
    
    def drawGrid(mode, canvas):
        gridDim = 10
        rows = mode.height // gridDim
        cols = mode.width // gridDim
        peach = mode.rgbString(245, 210, 190)
        for i in range(rows):
            canvas.create_line(0, i*gridDim, mode.width, i*gridDim, fill = peach, width = 1)
        for j in range(cols):
            canvas.create_line(j*gridDim, 0, j*gridDim, mode.height, fill = peach, width = 1)

    def redrawAll(mode, canvas):
        #background
        tan = mode.rgbString(250, 240, 230)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = tan)
        mode.drawGrid(canvas)
        #game
        y = mode.cy
        y -= mode.scrollY
        canvas.create_oval(mode.cx - mode.r, y - mode.r,
                            mode.cx + mode.r, y + mode.r, 
                            fill = 'blue')
        g = mode.currentPlat[1] + mode.height/2
        g -= mode.scrollY
        canvas.create_line(0, g, mode.width, g)
        mode.drawMonster(canvas)
        mode.drawPlatform(canvas)
        mode.drawBullet(canvas)
        mode.drawRotatePlatform(canvas)
        mode.drawSpringPowerUp(canvas)
        mode.drawScore(canvas)

class InstructionMode(Mode):
    def redrawAll(mode, canvas):
        font = 'Arial 12 bold'
        canvas.create_text(mode.width/2, 150, text='Instructions', font='Arial 26 bold')
        canvas.create_text(mode.width/2, 250, 
                            text='1. Use left and right arrow keys to move', font=font)
        canvas.create_text(mode.width/2, 300, 
                            text='2. Use up and down arrow keys to shoot, and "A" and "D" keys to change shoot angles ', font=font)
        canvas.create_text(mode.width/2, 350, 
                            text="3. Stay on the platforms, and don't let the monster catch you", font=font)
        canvas.create_text(mode.width/2, 450, 
                            text='Press "M" for Start Menu, "S" to start the game', font=font)
    
    def keyPressed(mode, event):
        if (event.key == 'm' or event.key == 'M'):
            mode.app.setActiveMode(mode.app.splashScreenMode)
        elif (event.key == 's' or event.key == 'S'):
            mode.app.setActiveMode(mode.app.gameMode)

class GameOverMode(Mode):
    def rgbString(mode, red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)
    
    def drawGrid(mode, canvas):
        gridDim = 10
        rows = mode.height // gridDim
        cols = mode.width // gridDim
        peach = mode.rgbString(245, 210, 190)
        for i in range(rows):
            canvas.create_line(0, i*gridDim, mode.width, i*gridDim, fill = peach, width = 1)
        for j in range(cols):
            canvas.create_line(j*gridDim, 0, j*gridDim, mode.height, fill = peach, width = 1)

    def redrawAll(mode, canvas):
        #background
        tan = mode.rgbString(250, 240, 230)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = tan)
        mode.drawGrid(canvas)
        #text
        font1 = 'Arial 30'
        font2 = 'Arial 16'
        canvas.create_text(mode.width/2, mode.height/2, text='game over', font=font1)
        canvas.create_text(mode.width/2, 350, text='press any key to restart', font=font2)
    
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = GameMode()
        app.setActiveMode(app.splashScreenMode)
        app.gameOverMode = GameOverMode()
        app.instructionMode = InstructionMode()
        app.timerDelay = 10

mode = MyModalApp(width=400, height=600)
