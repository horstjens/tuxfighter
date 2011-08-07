#!/usr/bin/env python
#file: TuxFighter52b.py
TuxFighterVersion = 54

"""
 _____           _____ _       _     _            
|_   _|   ___  _|  ___(_) __ _| |__ | |_ ___ _ __
  | || | | \ \/ / |_  | |/ _` | '_ \| __/ _ \ '__|
  | || |_| |>  <|  _| | | (_| | | | | ||  __/ |
  |_| \__,_/_/\_\_|   |_|\__, |_| |_|\__\___|_|
                         |___/


An overoptimistic attempt to write a pygame tutorial/book for kids.

This game is written 2006 by Horst JENS and is a free and open source game,
licensed under the GNU General Public License (GPL) since 2/2006;
see GPL.txt for copyright. It is allowed to modify and re-publish this
game as long as ist stay free and open source and GPL-Licensed.
For license questions or comments  contact me at
pygamebook@gmail.com, i like email.
"""


import os, pygame, math, random, string, sys, time, webbrowser   
from pygame.locals import *


mydir = os.getcwd() # get current working directory, the directory where the TuxFighter.py file itself is located
datadir = os.path.join(mydir, 'data') #directory for all the bitmaps, sounds is called datadir

if os.name == 'posix':
    print 'unix/linux detected' # try to import modding.py and load topten and ini from ~/.TuxFighter
    sys.path.append(os.environ["HOME"])
    sys.path.append(os.path.join(os.environ["HOME"], '.TuxFighter'))
    tuxhomedir = os.path.join(os.environ["HOME"], '.TuxFighter')
    #print "my active directory is: ", mydir
    try:
        from TuxFighter_modding_TuxHome import * # try to import the modding file from the tuxhomedir
        print "modding file imported. Eartaccel: ", str(EARTHACCEL)
        os.chdir(tuxhomedir)
    except:
        print 'konnte nicht von .TuxFighter importieren'
        os.chdir(os.environ["HOME"])
        os.mkdir('.TuxFighter')
        os.chdir('.TuxFighter')
        tuxhomedir = os.getcwd()
        #have to copy the modding file
        import shutil
        # for non-debian:
        shutil.copy(os.path.join(mydir, 'TuxFighter_modding.py'), os.path.join(tuxhomedir, 'TuxFighter_modding_TuxHome.py'))
        # for debian only:
        # shutil.copy(os.path.join('/usr/games/', 'TuxFighter_modding.py'), os.path.join(tuxhomedir, 'TuxFighter_modding_TuxHome.py'))            
        print 'i made a copy of the modding file'
        from TuxFighter_modding_TuxHome import *
        print "modding file imported. Earthaccel is now: " , str(EARTHACCEL)
else:
    print 'Mac or Windows detected'
    from TuxFighter_modding import *
    print "modding file imported. Earthaccel = " + str(EARTHACCEL)
GRAD = math.pi / 180 # 2 * pi / 360   # 

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit, "Sorry, extended image module required"
#check if pygame version is too low
if pygame.ver < "1.7.1release":
    print "Your pygame version is ", pygame.ver
    print "You need Version 1.7.1 or better. Look at www.pygame.org"
    xx = raw_input("press enter")
    raise SystemExit, "pygame version too low"
# check if python version is too low
if sys.version < "2.4.2":
    print "Your python version is ", sys.version
    print "You need Version 2.4.2 or better. Look at www.python.org"
    xx = raw_input("press enter")
    raise SystemExit, "python version too low"


#--- classes ---
class dummysound:
    def play(self):
        pass

        
class Player(pygame.sprite.Sprite):
    images = []
    
    def __init__(self, SCREENRECT, MouseControl):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[2]   # tux with a 2 on the belly 
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.area = SCREENRECT
        self.speed = [0.0,0.0]
        self.vpos = [(SCREENRECT.width/2)+0.0, (SCREENRECT.height/2)+0.0]
        self.dizzy = 0
        self.drehen = 0           # The angle of the original image
        self.rotieren = 0         # Direction of rotation: 0, -1 or +1
        #self.breit = 0
        self.original = self.image
        # always write 'False' or 'True', never write 'false' or 'true'
        self.randkontakt = False  # is tux contacting the wall of the playfield ?
        self.schublinks = False   # thrust left 
        self.schubrechts = False  # thrust right
        self.schuboben = False    # thrust up
        self.schubunten = False   # thrust down
        #self.drehlinks = False    # rotate counter-clockwise
        #self.drehrechts = False   # rotate clockwise
        self.faktor = TUX_SLOW    # The 'normal' Speed of Tux
        self.eyechange = False    # Flag to change the Eyecolor of Tux
        #self.ff = False           # fast forward !
        self.imageindex = 0
        self._walk()              # let him go his first step (ugly code?)
        self.lastimage = self.images[2] # the last actual image
        self.MouseControl = MouseControl
        self.serialhemp = 0
        self.stoned = False
        self.actualstoned_sec = 0.0
        self.totalstoned_sec = 0.0
        self.time0 = time.time()
        self.timedelta = 0.0
        self.MaxMinusLenRaketen = 2
        self.ubuntu = False
        self.time0_u = time.time()
        self.time_u = 0.0
        self.ubuntus = 0
        self.udelta = 0.0 # delta angle for Small Ubuntus
        self.hdelta = 0.0 # dekta abgke for Small Hemps
        
    def update(self):
        # check ubuntu protection
        if self.ubuntu:
            self.time_u = time.time() - self.time0_u
            if self.time_u > UBUNTU_MAX_SEC or self.ubuntus < 1:
                self.ubuntu = False
                self.ubuntus = 0
            else:
                # still ubuntu-protected, paint little ubuntus circling around Tux
                for ubunty in range(1,self.ubuntus+1):
                    self.udelta += (UBUNTU_MAX_SEC - self.time_u) / UBUNTU_MAX_SEC
                    SmallSprite(1, self.vpos, (360 / self.ubuntus) * ubunty , self.udelta , TUX_RADIUS * 1.3)
        # increase stoned sec if still stoned
        if self.stoned:
            self.timedelta =  time.time() - self.time0
            self.time0 = time.time()
            self.actualstoned_sec += self.timedelta
            self.totalstoned_sec += self.timedelta
            if self.actualstoned_sec > STONED_MAX_SEC:
                # no more stoned
                self.stoned = False
                self.serialhemp = 0
                self.actualstoned_sec = 0.0
            else:
                # still stoned, paint little hemps around Tux
                for hempy in range(1,self.serialhemp+1):
                    self.hdelta += (STONED_MAX_SEC - self.actualstoned_sec) / STONED_MAX_SEC
                    SmallSprite(0, self.vpos, (360 / self.serialhemp) * hempy , -self.hdelta , TUX_RADIUS)
        #"walk or spin, depending on the player state"
        # first resolve noammo-problematic, after that take care for red eyes
        
        if 0 <= (self.MaxMinusLenRaketen) < 4:
            self.imageindex = 2 * (self.MaxMinusLenRaketen)
        elif (self.MaxMinusLenRaketen) < 0:
            self.imageindex = 0                 # no rockets aviable for tux
        else:
            self.imageindex = 8                 # tux with bomb 
        if self.faktor != TUX_SLOW:             # red eyes for fast tux
            self.imageindex += 1 
        #print self.imageindex   
        self.original = self.images[self.imageindex]
            
        if self.original != self.lastimage:
            self._spin()# let rotate the actual image
            self.lastimage = self.original
             
        if self.schublinks or self.schubrechts or self.schuboben or self.schubunten:
            self._walk()   
        else:
            self.speed = [0.0,0.0] # no schub (=thrust), so no speed
        #self._walk()
        if self.MouseControl:
            self._spin()
        else:
            if self.rotieren != 0:
                self._spin()   
    
    def _walk(self):
        "move Tux around"
        newpos = self.rect.move((self.speed))
        self.speed = [0.0,0.0] # reset Speed
        
        if self.schublinks == True:
            self.speed[0] += -math.cos(self.drehen*GRAD)
            self.speed[1] += math.sin(self.drehen*GRAD)
        if self.schubrechts == True:
            self.speed[0] += math.cos(self.drehen*GRAD)
            self.speed[1] += -math.sin(self.drehen*GRAD)
        if self.schuboben == True: # forward is generally faster than other directions
            self.speed[0] += -math.sin(self.drehen*GRAD) * self.faktor 
            self.speed[1] += -math.cos(self.drehen*GRAD) * self.faktor
        if self.schubunten == True:
            self.speed[0] += math.sin(self.drehen*GRAD)
            self.speed[1] += math.cos(self.drehen*GRAD)
            
        # Contact with walls ?
        self.randkontakt = 0 # lets assume there is no contact so far
        if self.rect.left < self.area.left: 
            if self.speed[0] < 0:
                self.speed[0] = 0
        if self.rect.right > self.area.right:
            if self.speed[0] > 0:
                self.speed[0] = 0
        if self.rect.top < self.area.top:
            if self.speed[1] < 0:
                self.speed[1] = 0
        if self.rect.bottom > self.area.bottom:
            if self.speed[1] > 0:
                self.speed[1] = 0
        self.vpos[0] = self.vpos[0] + self.speed[0]
        self.vpos[1] = self.vpos[1] + self.speed[1]
        self.rect.center = round(self.vpos[0],0), round(self.vpos[1],0)
        
    def _spin(self):
        "rotate tux"
        center = self.rect.center
        
        if self.MouseControl:      # mouse code
            # compute where the mouse is and where the player is
            MausPos = pygame.mouse.get_pos()
            MyPos = self.rect.center
            # Get Angle so that Player face the mouse
            dx = MyPos[0] - MausPos[0]
            dy = MyPos[1] - MausPos[1]
            # secure minimum distant between mouse and Player
            #if (abs(dx) > self.rect.width/3) or (abs(dy) > self.rect.height/3):
            Mauswinkel = math.atan2(dx, dy) *180 / math.pi # aus dem modul math
                # print Mauswinkel, self.drehen
                # it is all ok as long as Mauswinkel dont go over 180
                # because then it becomes -180 and start messing around
                # Mouswinkel never leave the 180 range, it was self drehen who did
                # it...what a jerk
            if self.drehen > 180:
                self.drehen = -179
            if self.drehen < -180:
                self.drehen = 179
            # this whole codeblock needs a re-do   
            if abs(Mauswinkel) + abs(self.drehen) <= 180:
                if Mauswinkel > self.drehen:
                    self.rotieren = 1
                else:
                    self.rotieren = -1
            else:       
                if (self.drehen > 0 and Mauswinkel > 0) or (self.drehen < 0 and Mauswinkel < 0):
                    if Mauswinkel > self.drehen: 
                        self.rotieren = 1
                    else:
                        self.rotieren = -1
                else:
                    if Mauswinkel > 0: 
                        self.rotieren = -1
                    else:
                        self.rotieren = 1
                    
                    
        # keyboard control
        if self.drehen >= 360:
            self.drehen = 0
        elif self.drehen <= -360:
            self.drehen = 0
        else:
            if self.faktor != TUX_SLOW:
                self.drehen = self.drehen + self.rotieren * PLAYER_ROTATION_SPEED_SLOW
                # ok,ok: the meaning of this is: if tux is slow, he can rotate fast and vice versa
            else:   
                self.drehen = self.drehen + self.rotieren * PLAYER_ROTATION_SPEED # ugly if then code ?
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.drehen)
        self.rect = self.image.get_rect(center=center)
    
    def askpos(self):
        return self.vpos # returns the position of tux
    
    def askdreh(self):
        return self.drehen # returns the angle of tux
    
    def askspeed(self):
        return self.speed # returns the speed of tux
    
    def askserialhemp(self):
        return self.serialhemp
    
    def askubuntu(self):
        return self.ubuntu
    def askubuntupercent(self):
        return (UBUNTU_MAX_SEC - self.time_u) / UBUNTU_MAX_SEC
        #return self.time_u / UBUNTU_MAX_SEC
    
    def addhemp(self):
        self.serialhemp += 1
        self.time0 = time.time()
        self.actualstoned_sec = 0.0
        self.stoned = True
        
    def addubuntu(self, number=TUX_DEFAULTUBUNTUS):
        self.ubuntu = True
        self.time0_u = time.time()
        self.ubuntus += number
        
    def removeubuntu(self, number=1):
        self.ubuntus -= number
        #print self.ubuntus
        
    def setMaxLenRaketen(self, MaxMinusLenRaketen):
        self.MaxMinusLenRaketen = MaxMinusLenRaketen
        
    def asktotalstonedsec(self):
        return self.totalstoned_sec
    
    def askactualstonedpercent(self):
        #return self.actualstoned_sec / STONED_MAX_SEC
        return (STONED_MAX_SEC - self.actualstoned_sec) / STONED_MAX_SEC
    
    def askstoned(self):
        return self.stoned
    
    def askheadcenter(self, clockwise=True):
        if clockwise: # drehen normally + 90. but a bit more or less to create bubbles near ears of Tux
            return [self.vpos[0] +  math.cos(GRAD * (self.drehen+99))*TUX_HEADCENTER , self.vpos[1] - math.sin(GRAD * (self.drehen+99))*TUX_HEADCENTER ]
        else:
            return [self.vpos[0] +  math.cos(GRAD * (self.drehen+81))*TUX_HEADCENTER , self.vpos[1] - math.sin(GRAD * (self.drehen+81))*TUX_HEADCENTER ]            
    
    def askbellycenter(self, clockwise=True): # should be named: ask assholecenter
        if clockwise:
            return [self.vpos[0] +  math.cos(GRAD * (self.drehen+295))*(TUX_BELLYCENTER+35)*2 , self.vpos[1] - math.sin(GRAD * (self.drehen+295))*(TUX_BELLYCENTER+35)*2 ]
        else:
            return [self.vpos[0] +  math.cos(GRAD * (self.drehen+245))*(TUX_BELLYCENTER+35)*2 , self.vpos[1] - math.sin(GRAD * (self.drehen+245))*(TUX_BELLYCENTER+35)*2 ]            
    
##    def breit(self):
##        self.rect = self.rect.inflate(30,0)
##        self.image = self.images[2].convert()
        
class Goodie(pygame.sprite.Sprite):
    '''a goodie floats around and is maybe picked up by the Player.
       after some time the goodie disappear'''
    images = []
    def __init__(self, SCREENRECT):
        #print "i am alive"
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.age = 0.0
        self.age0 = time.time()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.area = SCREENRECT
        self.x = 0
        self.y = 0
        self.text = "surprise"
        self.rect.center = [random.randint(0, self.area.width),
                            random.randint(0, self.area.height)]
    def asktext(self):
        return self.text
        
    def askpos(self):
        return self.rect.center
    
    def update(self):
        self.age = time.time() - self.age0
        if self.age > GOODIE_SURPRISETIME_SEC and self.text == "surprise":
            Mitte = self.rect.center
            self.text = random.choice(("ubuntu", "hemp", "wine", "debian"))
            if self.text == "hemp":
                self.image = self.images[1]
            elif self.text == "debian":
                self.image = self.images[2]
            elif self.text == "wine":
                self.image = self.images[3]
            elif self.text == "ubuntu":
                self.image = self.images[4]
            self.rect = self.image.get_rect()
            self.rect.center = Mitte
        if self.age > GOODIE_LIFETIME_SEC + GOODIE_SURPRISETIME_SEC:
            self.kill()
        self.x = random.choice(( -1, 0,1)) # goes left, right or not at all
        self.y = random.choice(( -1, 0,1)) # goes up, down or not at all
        self.x = self.x * GOODIE_FAKTOR # goes left, right or not at all
        self.y = self.y * GOODIE_FAKTOR # goes up, down or not at all
        # Move Alien
        self.rect.move_ip(self.x, self.y)
        # bounce on Wall ?
        if self.rect.top < self.area.top:
            self.rect.top = self.area.top
            self.y = - self.y
        if self.rect.bottom > self.area.bottom:
            self.rect.bottom = self.area.bottom
            self.y = - self.y
        if self.rect.left < self.area.left:
            self.rect.left = self.area.left
            self.x = - self.x
        if self.rect.right > self.area.right:
            self.rect.right = self.area.right
            self.x = - self.x
         
    

class Alien(pygame.sprite.Sprite):
    faktor  = ALIEN_SLOW # only whole Numbers, no Decimals  !
    images = []
    def __init__(self, SCREENRECT):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.imageindex = 0  # ok
        self.imagemax =  len(self.images) - 1 # because index start with 0
        self.delta = 1         # the direction of the imagechange
        self.time0 = time.time()
        self.timeX = self.time0
        self.timeT = self.time0
        self.age = 0.0
        self.ageX = 0.0
        self.ageT = 0.0
        self.deltaX =  ALIEN_IMAGETIME / (self.imagemax + 1) # because index start with 0
        # ALIEN_THINKTIME 
        self.area = SCREENRECT
        # Player always spawn in the middle of screen, aliens outside the the wall
        zufall = random.choice([1,2,3,4]) # eckige Klammer ist wichtig !
        if zufall < 3:
            AlienStartX = random.randint(0,SCREENRECT.width - self.image.get_width())
            if zufall ==1: # north
                AlienStartY = - self.image.get_height() # out of screen
            else: # south
                AlienStartY = SCREENRECT.height + self.image.get_height()
        else:
            AlienStartY = random.randint(0, SCREENRECT.height - self.image.get_height())
            if zufall == 3: # west
                AlienStartX = - self.image.get_width()
            else: # east
                AlienStartX = SCREENRECT.width + self.image.get_width()
        self.rect.topleft = [AlienStartX, AlienStartY]

    def update(self):
        self.age = time.time() - self.time0 # if age too old, mutate alien into Boss ?
        self.ageX = time.time() - self.timeX
        if self.ageX > self.deltaX: # it is time for an imagechange !
            self.timeX = time.time() # reset timeX for alienimagechange
            if (self.imageindex == 0 and self.delta == -1 ) or (self.imageindex == self.imagemax and self.delta ==1):
                self.delta *= -1 # revert direction of imagechange
            self.imageindex += self.delta
            self.image = self.images[self.imageindex]  
        self.ageT = time.time() - self.timeT
        # for the first second, aliens move versus the center of the screen
        if self.ageT > ALIEN_THINKTIME and self.age > ALIEN_BORNTIME:
            self.timeT = time.time() # reset timeT for alienAI
            self.x = random.choice(( -1, 0,1)) # goes left, right or not at all
            self.y = random.choice(( -1, 0,1)) # goes up, down or not at all
            # now where is the player and where is the alien -> decide speed
            self.faktor = ALIEN_SLOW # reset
            if (self.rect.center[0] < PLAYER_X and self.x == 1) or (self.rect.center[0] > PLAYER_X and self.x == -1):
                self.faktor = ALIEN_FAST
            else:
                self.x = self.x * -1 # invers the x direction 
            if (self.rect.center[1] < PLAYER_Y and self.y == 1) or (self.rect.center[1] > PLAYER_Y and self.y == -1):
                if self.faktor == ALIEN_FAST:
                    self.faktor = ALIEN_VERYFAST # try to catch the player !
                else:
                    self.faktor = ALIEN_FAST
            else:
                self.y = self.y * -1
            self.x *= self.faktor # goes left, right or not at all
            self.y *= self.faktor # goes up, down or not at all
        elif self.age <= ALIEN_BORNTIME:
            # head to screencenter
            if self.rect.center[0] <= self.area.center[0]:
                self.x = 1
            else:
                self.x = -1
            if self.rect.center[1] <= self.area.center[1]:
                self.y = 1
            else:
                self.y = -1
        

        # Move Alien if no winetime is active
        if winetime == False or self.age <= ALIEN_BORNTIME:
            self.rect.move_ip(self.x, self.y)
        
        # Alien bounce on walls (after first second)?
        if self.age > ALIEN_BORNTIME:
            if self.rect.top < self.area.top:
                self.rect.top = self.area.top
                self.y = - self.y
            if self.rect.bottom > self.area.bottom:
                self.rect.bottom = self.area.bottom
                self.y = - self.y
            if self.rect.left < self.area.left:
                self.rect.left = self.area.left
                self.x = - self.x
            if self.rect.right > self.area.right:
                self.rect.right = self.area.right
                self.x = - self.x
         
    def askage(self):
        return self.age # returns the age of alien in seconds
    
    def askpos(self):
        return self.rect.center # returns the coordinates of the Alien

    def askrect(self):
        return self.rect #returns the current rectangle

class Explosion(pygame.sprite.Sprite):
    images = []
    def __init__(self, centerpos, small=False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.small = small
        if self.small == True:
            self.image=self.images[3]  # little boom
        else:
            self.image=self.images[0]  # big boom
        self.rect = self.image.get_rect(center = centerpos)
        self.time = time.time()
        self.time0 = time.time()
        self.imageindex = 0

    
    def update(self):
        if time.time() - self.time > EXPLOTIME:
            self.kill()
        elif time.time() - self.time0 > EXPLOCYCLE:
            self.time0 = time.time()
            self.imageindex += 1
            if self.imageindex > 2:
                self.imageindex = 0
            if self.small:
                self.image = self.images[self.imageindex + 3]
            else:
                self.image = self.images[self.imageindex]
                
class SmallSprite(pygame.sprite.Sprite):
    " a small dope/ubuntu symbol rotating around Tux to indicate that he is stoned/protected. lifetime is only one frame"
    images = []
    def __init__(self, spritenumber, centerpos, startgrad, angle , radius):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[spritenumber] # 0= hemp, 1=ubuntu
        self.rect = self.image.get_rect(center = (centerpos[0] + math.cos(GRAD * (startgrad + angle)) * radius,  centerpos[1] + math.sin(GRAD * (startgrad + angle))*radius))
        #note that in this frame the SmallDope is "born", update (and kill) will happen in the next frame
    def update(self):
        self.kill()
    def askpos(self):
        return self.rect.center
        
class BabyTux(pygame.sprite.Sprite):
    "a small cute Baby Tux doing eye candy in the highscore-List"
    images = []
    def __init__(self, startpos, xmin, xmax, redline, SCREENRECT):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.area = SCREENRECT
        self.image = self.images[0]
        self.vpos = [startpos[0] + 0.0, startpos[1] + 0.0]
        self.rect = self.image.get_rect(center = startpos)
        self.Status = "flydown"
        self.time0 = time.time()
        self.imagepointer = 1
        self.imageindex = 0
        self.redline = redline
        self.xmin = xmin
        self.xmax = xmax
        self.vel = [0.0,0.0]
        
        

    def update(self):
        if self.rect.left < 0 or self.rect.right > self.area.width:
            self.vel[0] = self.vel[0] * -1
        if self.Status == "flydown":
            if time.time() - self.time0 > BABYTUX_IMAGETIME/ len(self.images)-1: #the last image is special
                if self.imageindex == 0:
                    self.imagepointer = 1
                if self.imageindex == len(self.images)-1:
                    self.imagepointer = -1
                self.imageindex += self.imagepointer
                self.image = self.images[self.imageindex]
                self.time0 = time.time()
            #self.rect.move_ip(0,1)
            self.vel[1] += EARTHACCEL
            self.vpos[0] += self.vel[0]
            self.vpos[1] += self.vel[1]
            if self.vpos[1] + self.rect.height/2 > self.redline:
                self.vpos[1] = self.redline - self.rect.height/2
                bounce_sound.play()
                self.Status = "sit"
            self.rect.center = (round(self.vpos[0],0),round(self.vpos[1],0))
            
        elif self.Status == "sit":
            #self.image = self.images[5]
            if time.time() - self.time0 > BABYTUX_IDLETIME:
                self.time0 = time.time()
                self.image = self.images[random.choice((5,5,1,5,1))]
                    
        
        
    
##class AlienHerz(pygame.sprite.Sprite):
##    # This is the relevant hit-zone of an alien for the collison-detection
##    images = []
##    def __init__(self, centerpos):
##        pygame.sprite.Sprite.__init__(self, self.containers)
##        self.image = self.images[0]
##        self.rect = self.image.get_rect(center = centerpos)
##    
##    def update(self):
##        self.kill()

            

class Rakete(pygame.sprite.Sprite): 
    faktor = ROCKET_SPEED
    images = []
    Rpos = [] # virtual position
    speed = []
    dreh = 0  # angle
    def __init__(self, SCREENRECT, pos, dreh, speed, stoned=False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.imageindex = 0
        self.image = pygame.transform.rotate(self.images[self.imageindex], dreh)
        self.dreh = dreh
        self.speed = speed[:] # this command makes a COPY of the speed object
        self.speed0 = speed[:] # value between +- TUXFAST
        self.Rpos = pos[:]    # this command makes a COPY of the pos object
        self.rect = self.image.get_rect()
        self.rect.center = round(self.Rpos[0],0), round(self.Rpos[1],0)
        self.speed[0] += -math.sin(self.dreh*GRAD) * self.faktor
        self.speed[1] += -math.cos(self.dreh*GRAD) * self.faktor
        self.area = SCREENRECT
        self.bounce = 0 # counter for bouncing
        self.delta = random.random() * ROCKET_STONEDDELTARANGE - ROCKET_STONEDDELTARANGE / 2  # something between -1 and 1
        self.delta2 = random.random() * ROCKET_STONEDDELTARANGE2 - ROCKET_STONEDDELTARANGE2 / 2 # something between -.25 and .25
        self.age = 1
        self.ageR = 0.0
        self.ageRS = 0.0
        self.ageR0 = time.time()
        self.ageRS0 = time.time()
        self.stoned = stoned
       
        
    def update(self):
        self.age += 1
        self.ageR = time.time() - self.ageR0
        if self.ageR > ROCKET_TUXSAFETIME_SEC and self.imageindex == 0: #check if rocketcolor need changing
            if self.stoned:
                self.imageindex = 2 # stoned, green dangerous rocket (can harm tux)
            else:
                self.imageindex = 1 # dangerous red rocket (can harm tux)
            self.image = pygame.transform.rotate(self.images[self.imageindex], self.dreh) # change Rocket Color
        if self.stoned:  # make funny stuff with rocket
            self.ageRS = time.time() - self.ageRS0 
            #if self.age % 60 == 0: # exactly every 60.th frame
            if self.ageRS > ROCKET_STONEDIRCHANGETIME: # change speed and direction of record
                self.ageRS0 = time.time() # reset timer for stoned directionchange
                self.delta = random.random() * ROCKET_STONEDDELTARANGE - ROCKET_STONEDDELTARANGE / 2  # something between -1 and 1
                self.delta2 = random.random() * ROCKET_STONEDDELTARANGE2 - ROCKET_STONEDDELTARANGE2 / 2 # something between -.25 and .25
            # stoned changes for every frame    
            self.dreh += self.delta # every frame there is a slight direction change
            if self.delta != 0:    
                self.image = pygame.transform.rotate(self.images[self.imageindex], self.dreh)
            self.faktor += self.delta2  # change for speed
            self.speed0[0] *= ROCKET_STONEDFACTORFACTOR      # change for initial speed
            self.speed0[1] *= ROCKET_STONEDFACTORFACTOR
            self.speed[0] = self.speed0[0] + -math.sin(self.dreh*GRAD) * self.faktor
            self.speed[1] = self.speed0[1] + -math.cos(self.dreh*GRAD) * self.faktor
            self.rect = self.image.get_rect()
            self.rect.center = round(self.Rpos[0],0), round(self.Rpos[1],0)
        self.fly()
    
    def askbounce(self):
        return self.bounce

    def askageR(self):
        return self.ageR
    
    def askstoned(self):
        return self.stoned
    
    def askpos(self):
        #return self.rect.center
        return self.Rpos

    def askrect(self):
        return self.rect #returns the current rectangle
    
    def askdreh(self):
        return self.dreh
    
    def bouncewall(self, base):
        bounce_sound.play()
        self.dreh = base - self.dreh
        self.image = pygame.transform.rotate(self.images[self.imageindex], self.dreh)
        self.rect = self.image.get_rect()
        self.bounce +=1 # how often the rocket is bounced on the wall
        #print self.age, self.bounce

    def fly(self):
        #print self.rect.bottom, self.area.bottom
        if self.rect.left < self.area.left:       #left wall
            #if STONED or random.random() > ROCKET_BOUNCE:
            if random.random() > ROCKET_BOUNCE:
                Explosion(self.rect.center, True)
                self.kill()                         #no bounce
                wall_sound.play()
            else:
                self.speed[0] = - self.speed[0]     #bounce
                self.bouncewall(360)
        if self.rect.right > self.area.right:     #right wall
            if random.random() > ROCKET_BOUNCE:
                Explosion(self.rect.center, True)
                self.kill()                         #no bounce
                wall_sound.play()
            else:
                self.speed[0] = - self.speed[0]     #bounce
                self.bouncewall(360)
        if self.rect.top < self.area.top:         #top wall
            if random.random() > ROCKET_BOUNCE:
                Explosion(self.rect.center, True)
                self.kill()                         #no bounce
                wall_sound.play()
            else:
                self.speed[1] = - self.speed[1]     #bounce
                self.bouncewall(180)
        if self.rect.bottom > self.area.bottom:   #bottom wall
            if random.random() > ROCKET_BOUNCE:
                Explosion(self.rect.center, True)
                self.kill()                         #no bounce
                wall_sound.play()
            else:
                self.speed[1] = - self.speed[1]     #bounce
                self.bouncewall(180)
        ## calculate new position of rocket     
        self.Rpos[0] = self.Rpos[0] + self.speed[0] 
        self.Rpos[1] = self.Rpos[1] + self.speed[1] 
        self.rect.center = round(self.Rpos[0],0), round(self.Rpos[1],0)


##class Bomb(pygame.sprite.Sprite):
##    speed = 9
##    images = []
##    def __init__(self, alien):
##        pygame.sprite.Sprite.__init__(self, self.containers)
##        self.image = self.images[0]
##        self.rect = self.image.get_rect(midbottom=
##                    alien.rect.move(0,5).midbottom)
##
##    def update(self):
##        self.rect.move_ip(0, self.speed)
##        if self.rect.bottom >= 470:
##            Explosion(self)
##            self.kill()

class FlyScore(pygame.sprite.Sprite):
    def __init__(self, pos, FlyText):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(os.path.join(datadir, "freesansbold.ttf"), 14)
        self.color = Color('red')
        self.msg = FlyText
        #self.area = SCREENRECT
        #self.Rpos = pos[:] # make a copy of the pos object !!!
        self.image = self.font.render(self.msg, 1, self.color) #render 1 instead of 0
        self.rect = self.image.get_rect()
        #self.rect.center = round(self.Rpos[0],0), round(self.Rpos[1],0)
        self.rect.center = pos
        self.age = 0.0
        self.age0 = time.time()
        self.speed = 0.0



    def update(self): # write a new text if necessary
        self.age = time.time() - self.age0
        if self.age > FLYSCOREMAXAGE_SEC:
            self.kill() 
        if self.rect.top > 0: # only control if crossing top border
            self.speed +=  1-(self.age/FLYSCOREMAXAGE_SEC) # lesser and lesser
            if self.speed > 1:
                self.rect.move_ip(0,-1)
                self.speed -= 1 # decrease self.speed by 1
        
class TextSprite(pygame.sprite.Sprite):
    def __init__(self, pos, fontsize, message ):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(os.path.join(datadir, "freesansbold.ttf"), fontsize)
        self.color = Color('black')
        self.msg = message
        self.rect = (0,0,10,10)
        self.pos = pos
        self.old = "dummy-message"
        #self.desc = Description
        self.update() # write myself

        
    def setmsg(self, message):
        self.msg = message
    
    def update(self):
        if self.msg != self.old:
            self.image = self.font.render(self.msg, 1, self.color) # render 1 instead of 0
            self.rect = self.image.get_rect()
            self.rect.midleft = self.pos
#            if self.desc == False:
#                self.rect.topleft = self.pos
#            else:
#                self.rect.topright = self.pos
           
            
        



#--- general functions/procedures -----

def load_image(file, colorkey=None):
    "loads an image, prepares it for play, set Backgroundcolor at point 0,0 invisible if no second argument is given at calling "
    file = os.path.join(datadir, file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
    if colorkey is None:
        colorkey = surface.get_at((0,0))
        surface.set_colorkey(colorkey, RLEACCEL)
    elif colorkey <> -1:
        surface.set_colorkey(colorkey, RLEACCEL)
    return surface.convert()


def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


def load_sound(file):    
    if not pygame.mixer:
        return dummysound()
    file = os.path.join(datadir, file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print 'Warning, unable to load,', file
    return dummysound()

#def load_music(file):
#    if not pygame.mixer:
#        return dummysound()
#    file = os.path.join(datadir, file)
#    try:
#        music = pygame.mixer.music.load(file)
#        return music
#    except pygame.error:
#        print 'Warning, unable to load,',file
#    return dummysound()

#def pygameinit(winstyle):
def pygameinit(winstyle, SCREENRECT):
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    return screen

def back(screen, SCREENRECT):
    background = pygame.Surface(SCREENRECT.size)   
    bgdtile = load_image('background.jpg', -1)  # -1 avoid conversion to transparent background    
    # .............. tiles many times a small image ........
    #for x in range(0, SCREENRECT.width, bgdtile.get_width()):
    #    for y in range(0, SCREENRECT.height, bgdtile.get_height()):
    #        background.blit(bgdtile, (x, y))
    # ............... scale image .......................
    background = pygame.transform.scale(bgdtile, (SCREENRECT.width, SCREENRECT.height))
    screen.blit(background, (0,0))
    pygame.display.flip() # draw it now !
    return background
    
def menu(SCREENRECT, screen, menuentrys, selected=0, sound=None, leavehalfscreenfree = False):
    while True:
        #drawmenu(SCREENRECT, screen, menuentrys, selected)
        m_e = 0
        y = 0
        Base = 1.0
        if leavehalfscreenfree == True:
            y = .5
            Base = .5
        for menuentry in menuentrys:
            y += Base/(len(menuentrys) + 1) # because 0 < y < 1 ! To make a decimal, use a decimal      
            menu_box(SCREENRECT, screen, menuentry, y, (m_e==selected)) # (x==1) is True if x ==1, else it is False
            m_e += 1 # counter for the menupoint
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                return -1
            elif event.type == KEYDOWN:
                soundeffect = sound
                if event.key == K_ESCAPE:
                    return -1
                if event.key == K_RETURN or event.key == K_KP_ENTER: 
                    soundeffect.play() 
                    return selected
                if event.key == K_UP:
                    selected -= 1
                    soundeffect.play() 
                    if selected < 0:
                        selected = len(menuentrys) - 1 # cycle throug menuentrys
                if event.key == K_DOWN:
                    selected += 1
                    soundeffect.play() 
                    if selected > len(menuentrys) -1: # cycle throug menuentrys
                        selected = 0   

  
  
def menu_box(SCREENRECT, screen, message, y = .5, strongBorder=False):
    "Draw a menupoint of a menusystem, with text message at height y (.5 = center) "
    font = pygame.font.Font(os.path.join(datadir, "freesansbold.ttf"), 16)
    rect = pygame.Rect([0,0, SCREENRECT.width * .9, 27])
    boxcenter = (int(SCREENRECT.width/2), int(SCREENRECT.height*y))
    rect.center = boxcenter
    if strongBorder == True:
        pygame.draw.rect(screen, (210,48,48), rect, 0) 
        pygame.draw.rect(screen, (255,255,220),rect,4)
        if len(message) != 0:
            screen.blit(font.render(message, 1, (255,255,220)), (rect.left+5, rect.top + 3)) 
    else:
        pygame.draw.rect(screen, (120,24,24), rect, 0)
        pygame.draw.rect(screen, (220,255,64),rect,4)
        if len(message) != 0:
            screen.blit(font.render(message, 1, (220,255,64)), (rect.left+5,rect.top +3) )

        
def ask(SCREENRECT, screen, question):   # from pygame newsgroup
    "ask(screen, question) -> answer"
    pygame.font.init()  
    text = ""
    #display_box(screen, question + ": " + text)
    menu_box(SCREENRECT, screen, question + ": " + text)
    pygame.display.flip()
    while True:
        pygame.time.wait(50)
        #event = pygame.event.poll()
        for event in pygame.event.get():		
            if event.type == QUIT:
                sys.exit()	 
            elif event.type != KEYDOWN:
                continue
            elif event.key == K_BACKSPACE:
                text = text[0:-1]
            elif event.key == K_RETURN or event.key == K_KP_ENTER:
                return text
            else:
                text += event.unicode.encode("ascii")         
        #display_box(screen, question + ": " + text)
        menu_box(SCREENRECT, screen, question + ": " + text)
        pygame.display.flip()
           




def bigText(screen, background, SCREENRECT, msg, fontsize, y, flip, screenonly=False, yoffset=0):
    "displays big text (msg) like 'Game Over' in the middle of the screen. y (0<=y<=1) means % of max y"
    if pygame.font:
        font = pygame.font.Font(os.path.join(datadir, "freesansbold.ttf"), fontsize)
        text = font.render(msg, 1, (10,10,10))
        textpos = text.get_rect(centerx=SCREENRECT.width/2, centery=int(SCREENRECT.height*y)+yoffset)
        if screenonly == True:
            screen.blit(text,textpos)
        else:
            background.blit(text, textpos) 
            screen.blit(background, (0,0))
        if flip:
            pygame.display.flip()
           
def TableText(screen, background, SCREENRECT, msg, fontsize, y, yoffset=0, xoffset=0, xjust='center'):
    "displays a text element of a table. y is a fraction: 0.5=center. offsets in pixel"
    if pygame.font:
        font = pygame.font.Font(os.path.join(datadir, "freesansbold.ttf"), fontsize)
        text = font.render(msg, 1, (10,10,10))
        if xjust=='left': 
            textpos = text.get_rect(left=SCREENRECT.width/2 + xoffset, centery=int(SCREENRECT.height*y)+yoffset)
        elif xjust=='right':
            textpos = text.get_rect(right=SCREENRECT.width/2 + xoffset, centery=int(SCREENRECT.height*y)+yoffset)
        else:   
            textpos = text.get_rect(centerx=SCREENRECT.width/2 + xoffset, centery=int(SCREENRECT.height*y)+yoffset)
        background.blit(text, textpos)
        screen.blit(background, (0,0))
        

def startmenu(resx, resy, winstyle = 0):
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    #Initialize Everything
    again = False
    menuagain = False
    params = {}
    MOUSE = False
    JOYSTICK = False
    KEYSET = "WASD"
    CHEAT = False
    AI = "SEEK"
    ONSCREENHELP = "W,A,S,D =move; LEFT,RIGHT=spin; W+LSHIFT=fast, SPACE=fire, b=SmartBomb, p=Pause, ESC=menu"
    RESX = resx
    RESY = resy
    try:         # try to load and interpret ini-File:
        f = open("TuxFighter.ini")
        while True:
            zeile = f.readline()
            if len(zeile) == 0: #End of File
                break
            params[string.split(zeile,':')[0]] = string.rstrip(string.split(zeile,':')[1])
        f.close()
        if params.has_key("MOUSE"):
            if params['MOUSE'] == 'True':
                MOUSE = True
        if params.has_key("JOYSTICK"):
            if params['JOYSTICK'] == 'True':
                JOYSTICK = True
        if params.has_key("KEYSET"):
            if params['KEYSET'] == "CURSOR":
                KEYSET = "CURSOR"
        if params.has_key("CHEAT"):
            if params['CHEAT'] == 'True':
                CHEAT = True
        if params.has_key('AI'):
            if params['AI'] == 'RANDOM':
                AI = 'RANDOM'
        if params.has_key('ONSCREENHELP'):
            if len(params['ONSCREENHELP']) > 0:
                ONSCREENHELP = params['ONSCREENHELP']
        if params.has_key('RESX'):
            #print "found RESX"
            if int(params['RESX']) > 300:
                RESX = params['RESX']
                #print params['RESX']
        if params.has_key('RESY'):
            if int(params['RESY']) > 100:
                RESY = params['RESY']
        if params.has_key('FULLSCREEN'):
            if params["FULLSCREEN"] == "True":
                winstyle = FULLSCREEN
    except:
        print "ini file not found"
        params = {}
    pygame.init()
    # Set the display mode
    #winstyle = 0  # |FULLSCREEN
    #print params
    #print RESX, RESY
    SCREENRECT  = Rect(0, 0, int(RESX), int(RESY))
    screen = pygameinit(winstyle, SCREENRECT)
    background = pygame.Surface(SCREENRECT.size) 
    pygame.display.set_caption('TuxFighter menu')
    noammo_sound = load_sound('empty.wav')
    
    #---Main Menu Loop---
    #x = u""
    select = 0
    select2 = 2
    points = ["Start Single Player Game (Version: " + str(TuxFighterVersion)+")"]
    if MOUSE == False and JOYSTICK == False:
        points.append("Toggle Mouse/Keyboard/Joystick Control (now: Keyboard)")
    elif MOUSE == True and JOYSTICK == False:
        points.append("Toggle Mouse/Keyboard/Joystick Control (now: Mouse)")
    elif MOUSE == False and JOYSTICK == True:
        points.append("Toggle Mouse/Keyboard/Joystick Control (now :Joystick)")
    else:
        raise SystemExit,  "error: JOYSTICK and MOUSE selected."
    if KEYSET == 'WASD':
        points.append("Toggle Control Keys (now: W,A,S,D, SHIFT+W,left, right)")
    elif KEYSET == 'CURSOR':
        points.append("Toggle Control Keys (now: Cursorkeys, right CTRL, Keypad 0")
    else:
        print "KEYSET ERROR"
    if CHEAT == True:
        points.append("Toggle Cheat: now CHEATING mode is active")
    else:
        points.append("Toggle Cheat: now HONEST mode active")
    if AI == 'RANDOM':
        points.append("Toggle Enemy A.I. now: IGNORING the Player")
    else:
        points.append("Toggle Enemy A.I. now: HUNTING the Player")
    points.append("Set Screen Resolution...")
    points.append("Credits / Homepage / email")
    points.append("quit")
    SRpoints = ["Return to game menu",
                "Set Screen Resolution to  640 x  480",
                "Set Screen Resolution to  800 x  600",
                "Set Screen Resolution to 1024 x  768",
                "Set Screen Resolution to 1280 x 1024",
                "Set Screen Resolution to 1600 x 1200",
                "Set custom Resolution..."]
                
    if winstyle == FULLSCREEN:
        SRpoints.append("Toggle Fullscreen (Now: On)")
    else:
        SRpoints.append("Toggle Fullscreen (Now: Off)")
        
    SCpoints = ["Visit TuxFighter Homepage",
                "Send email to Horst",
                "Send email to Alexander",
                "Send email to Moritz",
                "Return to game menu"]
    while True:
        background = back(screen, SCREENRECT)
        screen.blit(background, (0,0))
        if again == True: 
            y = 0
        else:
            y = menu(SCREENRECT, screen, points, select, noammo_sound)
        #print "Resultat: ", y
        if y == 0:
            savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
            again = startgame(screen, background, SCREENRECT, MOUSE, JOYSTICK, KEYSET, CHEAT, ONSCREENHELP, AI, winstyle, noammo_sound) # 0 = winstyle
        elif y ==1:
            select = 1
            if MOUSE == False and JOYSTICK == True:
                MOUSE = True
                JOYSTICK = False
                points[1] =  "Toggle Mouse/Keyboard Control (now: Mouse)"
                ONSCREENHELP = "Mouse=spin, LEFT_CLICK=fire, RIGHT_CLICK=fast, MID_CLICK=SmartBomb, CURSOR=move, p=Pause, ESC=menu"    
            elif MOUSE == True and JOYSTICK == False:
                MOUSE = False
                points[1] =  "Toggle Mouse/Keyboard Control (now: Keyboard)"
                ONSCREENHELP = "W,A,S,D =move; LEFT,RIGHT=spin; W+LSHIFT=fast, SPACE=fire, p=Pause, ESC=menu, b=SmartBomb"
            else:
                MOUSE = False
                JOYSTICK = True
                points[1] =  "Toggle Mouse/Keyboard Control (now: Joystick)"
                ONSCREENHELP = "Joystick=spin, Button1=fire, Button3=fast, Button2=SmartBomb, CURSOR=move, p=Pause, ESC=menu"                    
        elif y ==2:
            select = 2
            if KEYSET == 'WASD':
                KEYSET = 'CURSOR'
                points[2] = "Toggle Control Keys (now: Cursorkeys, right CTRL, Keypad 0"
                ONSCREENHELP = "Numpad_0,R_CTRL,up,down =move; LEFT,RIGHT=spin; LSHIFT+up=fast, SPACE=fire, p=Pause, ESC=menu, b=Smartbomb"
            else:
                KEYSET = 'WASD'
                points[2] = "Toggle Control Keys (now: W,A,S,D, SHIFT+W,left, right)"
                ONSCREENHELP = "W,A,S,D =move; LEFT,RIGHT=spin; W+LSHIFT=fast, SPACE=fire, p=Pause, ESC=menu, b=SmartBomb"              
           # more keyboard setups ?
        elif y ==3:
            select = 3
            CHEAT = not CHEAT
            if CHEAT == True:
                points[3] = "Toggle Cheat: now CHEATING mode active"
            else:
                points[3] = "Toggle Cheat: now HONEST mode active"
        elif y ==4:
            select = 4
            if AI == "SEEK":
                AI = "RANDOM"
                points[4] = "Toggle Enemy A.I. now: IGNORING the Player"
            else:
                AI = "SEEK"
                points[4] = "Toggle Enemy A.I. now: HUNTING the Player"
        elif y == 5:
            select = 5
            while True:
                if menuagain == True:
                    return # the menu is called again
                background = back(screen, SCREENRECT)
                screen.blit(background, (0,0))
                y2 = menu(SCREENRECT, screen, SRpoints, 0, noammo_sound)
                if y2 == 0 or y2 == -1:  #-1:Escape was pressed in menu
                    break   # return to main menu                    
                else:
                    menuagain = True # the screenrect has been changed by the user
                    if y2 == 1:
                        SCREENRECT  = Rect(0, 0, 640, 480)
                        RESX = 640
                        RESY = 480
                        savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                        startmenu(RESX, RESY)
                    elif y2 == 2:
                        SCREENRECT  = Rect(0, 0, 800, 600)
                        RESX = 800
                        RESY = 600
                        savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                        startmenu(RESX, RESY)
                    elif y2 == 3:
                        SCREENRECT  = Rect(0, 0, 1024, 768)
                        RESX = 1024
                        RESY = 768
                        savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                        startmenu(RESX, RESY)
                    elif y2 == 4:
                        SCREENRECT  = Rect(0, 0, 1280, 1024)
                        RESX = 1280
                        RESY = 1024
                        savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                        startmenu(RESX, RESY)
                    elif y2 == 5:
                        SCREENRECT  = Rect(0, 0, 1600, 1200)
                        RESX = 1600
                        RESY = 1200
                        savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                        startmenu(RESX, RESY)
                    elif y2 == 6:
                        screen.blit(background, (0,0))
                        cx = int(ask(SCREENRECT,screen, "x-resolution in Pixel ? (min. 300)"))
                        cy = int(ask(SCREENRECT,screen, "y-resolution in Pixel ? (min. 100)"))
                        if cx >= 300  and cy >= 100 :
                            SCREENRECT = Rect(0, 0, cx, cy)
                            RESX = cx
                            RESY = cy
                            savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                            startmenu(RESX, RESY)                            
                            #screen = pygameinit(winstyle, SCREENRECT)
                    elif y2 == 7:
                        # winstyle = not winstyle didn't work because FULLSCREEN is a constant (-197123 or similar).
                        if winstyle == FULLSCREEN:
                            winstyle = 0
                        else:
                            winstyle = FULLSCREEN
                        savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, winstyle == FULLSCREEN)
                        startmenu(RESX, RESY, winstyle)
        elif y ==6:
            while True:
                select = 6 # credits
                background = back(screen, SCREENRECT)
                screen.blit(background, (0,0))
                bigText(screen, screen, SCREENRECT, "TuxFighter " + str(TuxFighterVersion),50,.1,False)
                bigText(screen, screen, SCREENRECT, "( a FREE and OPEN SOURCE Game under the GPL License since 2/2006 )", 18, .2, False)
                bigText(screen, screen, SCREENRECT, "Horst JENS...............Design & Code", 40, .3, False)
                bigText(screen, screen, SCREENRECT, "Alexander HUNGENBERG ....Support, Debian Packages", 23, .4, True)
                bigText(screen, screen, SCREENRECT, "Moritz Wilhelmy..........Fullscreen support", 23, .5, True)
                y3 = menu(SCREENRECT, screen, SCpoints, 0, noammo_sound, True)
                # after the only menupoint is selected, user is back in the big menu
                subjecttext = "TuxFighter %s, OS: %s ;" %(str(TuxFighterVersion), os.name)
                if y3 == 0: # visit homepage
                    webbrowser.open_new("http://sf.net/projects/pygamebook")
                elif y3 == 1:   #email to horst
                    mailtext = "i paid nothing for this game, but i *must* tell you:"
                    webbrowser.open_new("mailto:pygamebook@gmail.com?subject=" + subjecttext + "&body=" + mailtext)
                elif y3 == 2:   #email to alexander
                    mailtext = "the Force is strong with you, o Young One. Allow me to say:"
                    webbrowser.open_new("mailto:tuxfighter-deb@linnexhome.de?subject=" + subjecttext + "&body=" + mailtext)
                elif y3 == 3:  #email to Moritz Wilhelmy
                    mailtext ="thanks for the Fullscreen support!"
                    webbrowser.open_new("mailto:the.wulf.gang@googlemail.com?subject=" + subjecttext + "&body=" + mailtext)
                else:
                    break


        elif y ==7:
            select = 7
            break # quit
        elif y == -1:
            break # quit
         
    #print "i try to quit"    
    #pygame.quit() # that need more testing
    #print "but i still have life"
    return # quit

def savesettings(MOUSE, JOYSTICK, KEYSET, CHEAT, AI, ONSCREENHELP, RESX, RESY, FULLSCREEN):
    try: # try to save settings into .ini File
        f = file('TuxFighter.ini','w')
        f.write("MOUSE:" + str(MOUSE) +'\n')
        f.write("JOYSTICK:" + str(JOYSTICK) + '\n')
        f.write("KEYSET:" + KEYSET + '\n')
        f.write("CHEAT:" + str(CHEAT) + '\n')
        f.write("AI:" + AI + '\n')
        f.write("ONSCREENHELP:" + ONSCREENHELP + '\n')
        f.write("RESX:" + str(RESX) + '\n')
        f.write("RESY:" + str(RESY) + '\n')
        f.write("FULLSCREEN:" + str(FULLSCREEN) + "\n")
        f.close()
        print "settings saved into TuxFighter.ini at " + str(time.localtime())
    except:
        print "there was a problem at writing the TuxFighter.ini File at " + str(time.localtime())   


def init_star(direction, starpos, color,  links=False, rechts=False, unten=True, oben=False, rotatingarc = False):
    "creates new star values"
    arc = 45
    #oben = Tux fliegt nach oben
    #if oben == True and links == False and rechts == False and unten == False:
        #arc = 45
        #pass
    if oben == False and links == False and rechts == False and unten == True:   
        #arc = 45
        direction += 180
    elif oben == False and links == True and rechts == False and unten == False:
        #arc = 45
        direction += 90
    elif oben == False and links == False and rechts == True and unten == False:
        #arc = 45
        direction -= 90
    elif oben == False and links == False and rechts == False and unten == True:   
        #arc = 45
        direction += 180
    elif oben == True and links == True and rechts == False and unten == False:
        arc = 90
        direction += 45
    elif oben == True and links == False and rechts == True and unten == False:
        arc = 90
        direction -= 45
    elif oben == False and links == True and rechts == False and unten == True:
        arc = 90
        direction -= 270
    elif oben == False and links == False and rechts == True and unten == True:
        arc = 90
        direction += 270
    if rotatingarc:
        arc = ROTATINGARC
    dir = ((random.random()*GRAD*arc - GRAD*(arc/2)  + GRAD * direction))
    velmult = random.random()*1.6
    if not rotatingarc:
        velmult += .4 # non-rotating bubbles are faster than rotating bubbles
    vel = [math.sin(dir) * velmult, math.cos(dir) * velmult]
    age = [0.0]
    GhostFlag = [0]
    starcolor = [color]
    #return age, vel, WINCENTER[:], GhostFlag 
    return age, vel, starpos[:], GhostFlag, starcolor 


def draw_stars(surface, stars):
    "used to draw (and clear) the stars"
    #print stars
    localdirtystars = []
    for age, vel, pos, GhostFlag, color in stars:
        pos = (int(pos[0]), int(pos[1]))
        # starcolor = (255 ,FRAMECOLOR,255-FRAMECOLOR)
        b = int(age[0])+1 # each bubble gets older and older each frame
        if GhostFlag[0] != 0:   # it is a Ghostbubble ! draw nothing, just update it
            localdirtystars.append(Rect(pos[0]-b,pos[1]-b,1+2*b,1+2*b))
        elif age[0] <= 2:       # circle is so small, it is a point
            surface.set_at(pos, color[0]) 
            localdirtystars.append(Rect(int(pos[0])-2,int(pos[1])-2,5,5))
        else:
            pygame.draw.circle(surface, color[0], (int(pos[0]),int(pos[1])), int(age[0]/2), 1)
            localdirtystars.append(Rect(pos[0]-b,pos[1]-b,1+2*b,1+2*b))
    return localdirtystars
    
def move_stars(stars, SCREENRECT):
    "animate the stars"
    #stars.sort() # sort stars list for age
    for age, vel, pos, GhostFlag, color in stars:
        #print 'age',age,'vel',vel,'pos',pos,'GF',GhostFlag,'color', color
        age[0] = age[0] + .1
        #print pos[0]
        #print vel[0]
        pos[0] = pos[0] + vel[0]
        pos[1] = pos[1] + vel[1]
        if GhostFlag[0] == 2:
                stars.remove((age, vel,pos, GhostFlag, color)) # this ghost of a star no longer exist
        if GhostFlag[0] == 1: # star is already invisible 
            GhostFlag[0] = 2  # star is marked to be removed
        elif not (0 <= pos[0] <= SCREENRECT.width ) or not (0 <= pos[1] <= SCREENRECT.height) or (abs(vel[0]) <= STARSMINVELX and abs(vel[1]) <= STARSMINVELY):
            GhostFlag[0] = 1 # star is marked to be removed because he tryed to escape the screen
        else:                # stars become a bit slower
            vel[0] = vel[0] * .99
            vel[1] = vel[1] * .99
    return stars


def collision(TuxPos, TuxDreh, enemyrec):
    """ this function look if Tux is hit by an enemy REC into the head or into the belly. 
    returns 2 if hit in the head, 1 if hit in the belly else 0 """
    #bangbang = False
    headcenter = (int(TuxPos[0] +  math.cos(GRAD * (TuxDreh+90))*TUX_HEADCENTER) , int(TuxPos[1] - math.sin(GRAD * (TuxDreh+90))*TUX_HEADCENTER ))
    for controlpoint in range(1,(360/TUX_CONTROLANGLE)+1):
        if enemyrec.collidepoint( int(headcenter[0]+math.cos(GRAD * controlpoint * TUX_CONTROLANGLE)* TUX_HEADRADIUS), int(headcenter[1]-math.sin(GRAD * controlpoint * TUX_CONTROLANGLE) * TUX_HEADRADIUS)) == True:
            print "Hit in the Head"
            return 2
            #bangbang = True
            #break
    else:   # this part will be executed if the former for-loop was run trough without break
        bellycenter = (int(TuxPos[0] +  math.cos(GRAD * (TuxDreh+90))*TUX_BELLYCENTER) , int(TuxPos[1] - math.sin(GRAD * (TuxDreh+90))*TUX_BELLYCENTER ))
        for controlpoint in range(1,(360/TUX_CONTROLANGLE)+1):
            if enemyrec.collidepoint(int(bellycenter[0]+math.cos(GRAD * controlpoint * TUX_CONTROLANGLE)* TUX_BELLYRADIUS), int(bellycenter[1]-math.sin(GRAD * controlpoint * TUX_CONTROLANGLE) * TUX_BELLYRADIUS)) == True: 
                print "Hit in the belly"
                return 1
                #bangbang = True
                #break
    return 0

def arctimer(screen, arccolor, arcrect, howmuch,  polycolor):
    # This is my personal drawarc - function
    # because pygame.arc did not fill like i will , produceds artifacts and generally suck big time
    pygame.draw.circle(screen, arccolor, arcrect.center, arcrect.width/2, 0) # 0 fills circle
    poly=[arcrect.center, arcrect.midtop]
    # howmuch starts with 1, ends with 0
    # circle is filled with color, poly "eat" circle..first all, later less and less
    # 
    if howmuch > 7.0/8:
        poly.append(arcrect.topleft)
        poly.append(arcrect.midleft)
        poly.append(arcrect.bottomleft)
        poly.append(arcrect.midbottom)
        poly.append(arcrect.bottomright)
        poly.append(arcrect.midright)   
        poly.append(arcrect.topright)
    elif howmuch > 6.0 / 8:
        poly.append(arcrect.topleft)
        poly.append(arcrect.midleft)
        poly.append(arcrect.bottomleft)
        poly.append(arcrect.midbottom)
        poly.append(arcrect.bottomright)
        poly.append(arcrect.midright)   
    elif howmuch > 5.0/8:    
        poly.append(arcrect.topleft)
        poly.append(arcrect.midleft)
        poly.append(arcrect.bottomleft)
        poly.append(arcrect.midbottom)
        poly.append(arcrect.bottomright)
    elif howmuch > 4.0/8:
        poly.append(arcrect.topleft)
        poly.append(arcrect.midleft)
        poly.append(arcrect.bottomleft)
        poly.append(arcrect.midbottom)
    elif howmuch > 3.0/8:
        poly.append(arcrect.topleft)
        poly.append(arcrect.midleft)
        poly.append(arcrect.bottomleft)
    elif howmuch > 2.0/8:
        poly.append(arcrect.topleft)
        poly.append(arcrect.midleft)
    elif howmuch > 1.0/8:
        poly.append(arcrect.topleft)
    else:
        pass
    poly.append((arcrect.center[0] + math.cos(math.pi/2 + 2*math.pi*(howmuch))*(arcrect.width/2),arcrect.center[1] - math.sin(math.pi/2 + 2*math.pi*(howmuch))*(arcrect.height/2)))
    pygame.draw.polygon(screen, polycolor, poly, 0) # 0 = filled
    pygame.draw.circle(screen, (0,0,0), arcrect.center, arcrect.width/2+1, 1) # black border    
    # angle 0 start  at midleft and runs ofer topleft, midtop 
    # pygame.draw.arc(screen, (0,0,255), arcrect, math.pi/2, howmuch * 2 * math.pi + math.pi / 2, 8)

def startgame(screen, background, SCREENRECT, MOUSE=False, JOYSTICK=False, KEYSET="WASD",CHEAT=False,
              ONSCREENHELP="W,A,S,D =move; LEFT,RIGHT=spin; W+LSHIFT=fast, SPACE=fire, b=SmartBomb, p=Pause, ESC=menu",
              AI="SEEK",WINSTYLE = 0, soundeffect=None):
    #def main(winstyle=0):            
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    
    MAX_ALIENS = 2
    MAX_RAKETEN = 4
    SCORE = 0
    global PLAYER_X
    global PLAYER_Y
    global WINCENTER
    global winetime
    winetime = False
    winetime0 = time.time()
    FRAMECOLOR = 0
    FRAMECOLORDELTA = 1
    FPS = 0
    WINCENTER =[SCREENRECT.width/2, SCREENRECT.height/2]
    stars = []
    dirtystars = []
    #white = 255, 240, 200
    #black = 20, 20, 40
    #fastcolor = 140,20,40
    # --- important variables -----
    MouseControl = MOUSE
    JoystickControl = JOYSTICK
    if JoystickControl == True:
        pygame.joystick.init() # now the stick is initialized and send events 
        
        #let's turn on the joysticks just so we can play with em
        for stick in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(stick)
            j.init()
            print 'Enabled joystick: ' + j.get_name()
        if not pygame.joystick.get_count():
            raise SystemExit, "Sorry, no Joystick detcted"
    
    
    MAX_RAKETEN = 1
    MAX_ALIENS = 1
    PLAYER_X = 10 # for Alien AI
    PLAYER_Y = 10 # for ALIEN AI
    
    ALIEN_ODDS     = 200   #chances that a new alien appears (high number -> less chance)
    #BOMB_ODDS      = 60    #chances a new bomb will drop
    ALIEN_RELOAD   = 12    #frames between new aliens
    GAME_OVER = False
    POST_MORTEM = 60 # Frames after Death of Tux but before GAME OVER
    SHOTS_TO_ALIENS_RATIO = 2 # how many shots per alien on screen (>1 is easy, <1 is hard)
    BOUNCE_KING = 5 # if rocket hits after bouncing this number (or more often), extra bonus sound   
    SCORE = 0
    FRAGS = 0
    PAUSE = False
    PLAY_START = int(time.time())
    PLAY_END = int(time.time())
    PLAY_TIME = "0:00:00"
    #STONED_TIME = "0:00:00"
    #STONED_START = 0.0
    #STONED_END = 0.0
    STONED_SECS = 0.0
    #--- Highscorelist ---
    HIGHSCORE = []
    #STONED_MAX = 1200 # time in frames (60 Frames/second)
    #STONED_FRAMES = 0
    #STONED = False
    LASERARRAY = [] # array for the start and end pos of laser rays
    #LASERARRAYOLD = []
    LASERLENOLD = 0
    SCREENREPAINT = False
    GOODIETIME = time.time()
    dirty = [Rect(0,0,0,0)]
    laserdirty = []
    #olddirty = dirty[:]
    
    entry = ()
    try:
        f = file("topten.txt")
        while True:
            zeile = f.readline()
            if len(zeile) == 0:
                break
            x = string.split(zeile,',',4)
            entry = (int(x[0]),round(float(x[1]),1),x[2], round(float(x[3]),1),x[4][:-1])
            # the -1 avoid the /n in the namestring
            HIGHSCORE.append(entry)
        f.close()
    except:
        HIGHSCORE = [(10, 33, '0:02:00', 0, "Horst F. JENS"),
                     (8, 21, '0:01:00', 0,  "Horst JENS") ,
                     (7, 20, '0:00:30', 0, "Horst")]
        # score, hitquota, time, stonedquota, name
    LEN_RAKETEN = 0
    LEN_GOODIES = 0
    LEN_ALIENS = 0
    PLAYER_SHOTS = 0
    HITMATRIX = {0:0} # player has shot 0 directhits and 0 bounce(1x)
    
    #- debian rays
    #debianrays = []
    debianT0 = 0.0
    
    # --- important variables -----
    
    
    #Initialize Everything
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print 'Warning, no sound'
        pygame.mixer = None
    
    # Set the display mode
    winstyle = WINSTYLE  # |FULLSCREEN
    #bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    #screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, WINSTYLE, 32)
    
    screen = pygame.display.set_mode(SCREENRECT.size, WINSTYLE, bestdepth)
    
    
    #--- load files ---
    #Load images, assign to sprite classes
    #(do this before the classes are used, after screen setup)
    BabyTux.images = load_images('babytux1.png',
                                 'babytux2.png',
                                 'babytux3.png',
                                 'babytux4.png',
                                 'babytux5.png',
                                 'babytux6.png')
        
    Player.images = load_images('tux0.png','tux0red.png',
                                'tux1.png','tux1red.png',
                                'tux2.png','tux2red.png',
                                'tux3.png','tux3red.png',
                                'tux4.png','tux4red.png')
    
    Explosion.images = load_images('ex1.png',
                                   'ex2.png',
                                   'ex3.png',
                                   'ex1_small.png',
                                   'ex2_small.png',
                                   'ex3_small.png') # Keine eckige Klammer !!!!!!!
    #Alien.images = load_images('alien1.gif', 'alien2.gif', 'alien3.gif')
    Alien.images = load_images('winlogoh1.png',
                               'winlogoh2.png',
                               'winlogoh3.png')
    #                           'winlogo4.png')
    #Alien.images = load_images('bad_guy1.png', 'bad_guy1.png', 'bad_guy1.png')
    #Bomb.images = [load_image('bomb.gif')] # eckige Klammer weil nur ein Bild
    #Rakete.images = [load_image('rakete.png')] # detto
    Rakete.images = load_images('rakete.png',
                                'rakete2.png',
                                'rakete3.png')
    #AlienHerz.images = [load_image('alienHerz2.png')]
    Goodie.images = load_images('surprise.png',
                                'dope.png',
                                'debian.png',
                                'wine.gif',
                                'ubuntulogo.png')
    SmallSprite.images = load_images('dope_small.png',
                                  'ubuntulogo_small.png')
    #SmallUbuntu.images = [load_image('ubuntulogo_small.png')]
    #decorate the game window
    icon = pygame.transform.scale(Player.images[1], (32, 32)) # Redeye-Tux Icon
    pygame.display.set_icon(icon)
    pygame.display.set_caption("TuxFighter Version " + str(TuxFighterVersion))
    if MouseControl == True:
        pygame.mouse.set_visible(1) # Mouse visible
    else:
        pygame.mouse.set_visible(0) # Mouse invisible
    
    #load the sound effects
    global wall_sound
    #prosecco_sound = load_sound('wine.wav')
    wall_sound = load_sound('wall.wav')
    self_shot = load_sound('self_shot.wav')
    boom_sound = load_sound('boom.wav')
    rakete_sound = load_sound('car_door.wav')
    playerex_sound = load_sound('player_explsion.wav')
    cash_sound = load_sound('cash.wav')
    trommel_sound = load_sound('trommel.wav')
    global bounce_sound  # bounce is played in the rakete-update class
    bounce_sound = load_sound('bounce.wav')
    noammo_sound = soundeffect # parameter from startmenu
    goodie_shot_sound = load_sound('dope_shot.wav')
    goodie_pickup_sound = load_sound('mampf.wav')
    
    
    
    # Initialize Game Groups
    aliens = pygame.sprite.Group()
    raketen = pygame.sprite.Group()
    goodies = pygame.sprite.Group()
    smallsprites = pygame.sprite.Group()
    #babutuxys = pygame.sprite.Group()
    #bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    #lastalien = pygame.sprite.GroupSingle()
    #explosionen = pygame.sprite.Group()
    
    #alienHerze = pygame.sprite.GroupSingle()
    
    #assign default groups to each sprite class
    Player.containers = all
    BabyTux.containers = all
    Alien.containers = aliens, all
    Goodie.containers = goodies, all
    FlyScore.containers = all
    TextSprite.containers = all
    Rakete.containers = raketen, all
    #Bomb.containers = bombs, all
    Explosion.containers = all
    SmallSprite.containers = smallsprites, all
    #SmallUbuntu.containers = all
    #Score.containers = all
    
    #AlienHerz.containers = alienHerze, all
    
    
    #Create Some Starting Values
    #global score 
    alienreload = ALIEN_RELOAD
    kills = 0
    clock = pygame.time.Clock()
    
    
    #initialize our starting sprites
    player = Player(SCREENRECT, MouseControl)
    alien = Alien(SCREENRECT) #note, this 'lives' because it goes into a sprite group
    goodie = Goodie(SCREENRECT)
    #if pygame.font:
        #all.add(Score())
        #score = Score()
        #all.add(score)
        
    
    #while player.alive():
    Accel = False
    #Sekunden = 0
    #Sekunden = time.localtime()[5]
    #framecount = 0
    
    #--- UI Elements ---
    scoreP1 =   TextSprite((55,10),15,"0")
    kills =     TextSprite((125,10),15,"0")
    maxEnemys = TextSprite((255,10),15,"0")
    ammo =      TextSprite((335,10), 15, "2 / 2")
    fps =       TextSprite((425,10),15,"0")
    status =    TextSprite((525,10), 15, "clean")
    #status2 =   TextSprite((565.10), 15, "mortal")

    mitte = SCREENRECT.width / 2
    #def TableText(screen, background, SCREENRECT, msg, fontsize, y, yoffset=0, xoffset=0, xjust='center'):
    TableText(screen, background, SCREENRECT, "Score:",         15, 0, 10,50-mitte,"right")
    TableText(screen, background, SCREENRECT, "Kills:",         15, 0, 10,120-mitte,"right")
    TableText(screen, background, SCREENRECT, "max. Enemys:",   15, 0, 10,250-mitte,"right")
    TableText(screen, background, SCREENRECT, "Ammo:",          15, 0, 10,330-mitte,"right")
    TableText(screen, background, SCREENRECT, "Fps:",           15, 0, 10,420-mitte,"right")
    TableText(screen, background, SCREENRECT, "Status:",        15, 0, 10,520-mitte,"right")
    
    #--- onscreenhelp ---
    #Put Text On The Background, Centered
    bigText(screen, background, SCREENRECT, ONSCREENHELP, 14, 1, True, False, -10)   
    # red line above onscreenhelp
    pygame.draw.line(background, [255,0,0], (0,SCREENRECT.height - 20), (SCREENRECT.width, SCREENRECT.height -20), 2)
    # red line below score
    pygame.draw.line(background, [255,0,0], (0,20), (SCREENRECT.width,20),2)
    # red lines left and right
    #pygame.draw.line(background, [255,0,0], (20,0), (20,SCREENRECT.height),2)
    #pygame.draw.line(background, [255,0,0], (SCREENRECT.width -20,0), (SCREENRECT.width - 20, SCREENRECT.height),2)
    #pygame.draw.rect(background, [255,0,0], pygame.Rect(200,50,20,299),2) # just a test


    # red rect on screen to show alien spawn zone
    #szx = Alien.images[0].get_width()
    #szy = Alien.images[0].get_height()
    #pygame.draw.rect(background, [255,0,0], (szx, szy, SCREENRECT.width - 2 * szx, SCREENRECT.height - 2 * szy) , 2)

    #arcpen = 7
    arcrect = Rect(570,0,25,25) # the arc for being stoned
    arccolor = [40,255,40]
    urect = Rect(610,0,25,25)
    ucolor = [255,40,40]
    polycolor = (255,255,255) # color for outer edge of arctimers = white
    #polycolor = (0,255,0)


    #blit all this stuff into the screen
    screen.blit(background, (0,0))
    pygame.display.flip()
    
    
    #--- Main Loop ---
    while True:
        #clock.tick(60) 
        if MAXFPS == 0:
            clock.tick() # ask the clock for time once per frame
        else:
            clock.tick(MAXFPS) # maximal MAXFPS Frames per Second 
        fps.setmsg(str(round(clock.get_fps(),0)))
        Fire = False
        SmartBomb = False
        
        screen.blit(background, (0,0))
        # paint nice red circles out of Tux Ass
        if player.askstoned() == True:
            tuxcolor = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        elif Accel == True:
            tuxcolor = FASTCOLOR
        else:
            tuxcolor = SLOWCOLOR
        if player.schublinks == True or  player.schubrechts == True or player.schuboben == True or player.schubunten == True:
            if random.random() < TUX_NEWBUBBLE: # start a new bubble
                stars.append(init_star(player.askdreh(),player.askpos(),tuxcolor,player.schublinks, player.schubrechts, player.schubunten, player.schuboben))
        # paint bubbles if Tux is rotating
        tuxcolor = ROTATINGCOLOR
        if player.rotieren == -1:
            if random.random() < TUX_NEWBUBBLE: # start a new bubble
                stars.append(init_star(player.askdreh(),player.askheadcenter(True),tuxcolor,False, True, False, False, True))  
                stars.append(init_star(player.askdreh(),player.askbellycenter(True),tuxcolor,True, False, False, False, True))   
        elif player.rotieren == 1:
            if random.random() < TUX_NEWBUBBLE: # start a new bubble
                stars.append(init_star(player.askdreh(),player.askheadcenter(False),tuxcolor,True, False, False, False, True))  
                stars.append(init_star(player.askdreh(),player.askbellycenter(False),tuxcolor,False, True, False, False, True))               
        # paint nice bubble for each rocket        
        for rakete in raketen:
            if random.random() < ROCKET_NEWBUBBLE: # start a new bubble
                if rakete.askstoned() == True:
                    tuxcolor = random.randint(0,255), random.randint(0,255), random.randint(0,255)
                else:
                    tuxcolor = ROCKETCOLOR
                #print "rocketstar"
                stars.append(init_star(rakete.askdreh(), rakete.askpos(), tuxcolor))

        dirtystars = []
        stars = move_stars(stars, SCREENRECT)
        #if Accel == True: # different bubble color for fast tux
        dirtystars = draw_stars(screen, stars) # draw the stars, calculate updaterecs
        #else:
        #    dirtystars = draw_stars(screen, stars, slowcolor, FRAMECOLOR, player.askstoned()) # draw new
        #update all the sprites
        if PAUSE == False:
            #print all 
            all.update()
        WINCENTER = player.askpos()
        
        # test hitzones
        #print "pc:", player.askpos(), "pd:",player.askdreh(), "hc:", (player.askpos()[0] +  math.cos(GRAD * (player.askdreh()+90))*TUX_HEADCENTER , player.askpos()[1] - math.sin(GRAD * (player.askdreh()+90))*TUX_HEADCENTER )
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if (event.key == K_q) and (POST_MORTEM == 0): # Game over
                    return True
                if event.key == K_ESCAPE:
                    # display menu
                    return False
                    
                if event.key == K_p:
                    PAUSE = not PAUSE  # invert the PAUSE Flag: True / False
                    if PAUSE == True:
                        bigText(screen, background, SCREENRECT, "PAUSE",200,.5,True,True)
                    else:
                        bigText(screen, background, SCREENRECT, "",200,.5,True,False) # code not perfect: sprites overwrite the pause text
                    
                    
                if MouseControl or JoystickControl:
                    if event.key == K_LEFT:
                        player.schublinks = True
                    if event.key == K_RIGHT:
                        player.schubrechts = True
                    if event.key == K_UP:
                        player.schuboben = True
                    if event.key == K_DOWN:
                        player.schubunten = True
                    if event.key == K_RCTRL:
                        Accel = True
                else: # keyboard control
                    if event.key == K_SPACE:  
                        Fire = True               # fire
                    # ------------------------- Testing only ------------------------
                    #if event.key == K_t:
                    # ---------------------------------------------------------------
                    if event.key == K_b:         
                        SmartBomb = True          # Smartbomb
                    if event.key == K_LEFT:
                        if player.rotieren == -1:
                            player.rotieren = 0
                        else:
                            player.rotieren = 1   # rotate to the left
                    if event.key == K_RIGHT:
                        if player.rotieren == 1:
                            player.rotieren = 0
                        else:
                            player.rotieren = -1  # rotate to the right
                        
                    if KEYSET == "WASD":   
                        if event.key == K_a:
                            player.schublinks = True  # tux.speed[0] -= 1 # links
                        if event.key == K_d:
                            player.schubrechts = True # tux.speed[0] += 1 # rechts
                        if event.key == K_w:
                            player.schuboben = True   # tux.speed[1] -= 1 # rauf
                        if event.key == K_s:
                            player.schubunten = True  # tux.speed[1] += 1 # runter
                        if event.key == K_LSHIFT: 
                            Accel = True               # Acceleration
                    elif KEYSET == "CURSOR":
                        if event.key == K_RCTRL:
                            player.schublinks = True  # tux.speed[0] -= 1 # links
                        if event.key == K_KP0:
                            player.schubrechts = True # tux.speed[0] += 1 # rechts
                        if event.key == K_UP:
                            player.schuboben = True   # tux.speed[1] -= 1 # rauf
                        if event.key == K_DOWN:
                            player.schubunten = True  # tux.speed[1] += 1 # runter
                        #if event.key == K_LALT: 
                        if event.key == K_LSHIFT:
                            Accel = True               # Acceleration
                        
                        # uncomment this block to have alternate movement and acceleartion
            elif event.type == KEYUP:
                if MouseControl or JoystickControl:
                    if event.key == K_LEFT:
                        player.schublinks = False
                    if event.key == K_RIGHT:
                        player.schubrechts = False
                    if event.key == K_UP:
                        player.schuboben = False
                    if event.key == K_DOWN:
                        player.schubunten = False
                    if event.key ==  K_RCTRL:
                        Accel = False
                else: #keyboard control
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        player.rotieren = 0
                    if KEYSET == "WASD":    
                        if event.key == K_a:
                            player.schublinks = False
                        if event.key == K_d:
                            player.schubrechts = False
                        if event.key == K_w:
                            player.schuboben = False
                        if event.key == K_s:
                            player.schubunten = False
                        if event.key == K_LSHIFT:
                            Accel = False
                    elif KEYSET == "CURSOR":
                        if event.key == K_RCTRL:
                            player.schublinks = False
                        if event.key == K_KP0:
                            player.schubrechts = False
                        if event.key == K_UP:
                            player.schuboben = False
                        if event.key == K_DOWN:
                            player.schubunten = False
                        #if event.key == K_LALT:
                        if event.key == K_LSHIFT:   
                            Accel = False
                        
            #if MouseControl:    
            elif event.type == MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0] == True: #left mousebutton
                        Fire = True
                    else:
                        Fire = False
                    if pygame.mouse.get_pressed()[2] == True: #right mousebutton
                        Accel = True
                        if player.schuboben == False and player.schubunten == False:
                            player.schuboben = True
                    if pygame.mouse.get_pressed()[1] == True: #middle mousebutton
                        SmartBomb = True
                 
            elif event.type == MOUSEBUTTONUP:
                    if pygame.mouse.get_pressed()[2] == False:
                        Accel = False
                        if player.schuboben == True:
                            player.schuboben = False
                 
            #elif JoystickControl:
            elif event.type == JOYBUTTONDOWN:
                    #print "joybutton was pressed"
                    if j.get_button(0) == True: # left joybutton pressed
                        Fire = True
                    if j.get_button(1) == True: 
                        SmartBomb = True
            elif event.type == JOYAXISMOTION:
                    #print "Joystick axis motion detected"
                    if j.get_axis(1) < -0.8:
                        Accel = True
                        player.schuboben = True
                        player.schubunten = False
                    elif j.get_axis(1) < -0.5:
                        Accel = False
                        player.schuboben = True
                        player.schubunten = False
                    elif j.get_axis(1) > 0.5:
                        Accel = False
                        player.schuboben = False
                        player.schubunten = True
                    else:
                        Accel = False
                        player.schuboben = False
                        player.schubunten = False
                    if j.get_axis(0) > 0.5:
                        if player.rotieren == 1:
                            player.rotieren = 0
                        else:
                            #pass
                            player.rotieren = -1
                    elif j.get_axis(0) < -0.5:
                        if player.rotieren == -1:
                            player.rotieren = 0
                        else:
                            player.rotieren = 1 
                    else:
                        #pass
                        player.rotieren = 0


          
        # -------- End of for event in pygame - event --------------
           
        if Accel:  # if Accel == True:
            if player.faktor == TUX_SLOW:
                player.eyechange = True # Tux shall have red eyes
            player.faktor = TUX_FAST # let Tux run fast forward
        else:
            if player.faktor == TUX_FAST:
                player.eyechange = True
            player.faktor = TUX_SLOW            
            
        if Fire and player.alive():
            if len(raketen) < MAX_RAKETEN: # tux can fire 
                rakete_sound.play()
                rakete = Rakete(SCREENRECT, player.askpos(), player.askdreh(), player.askspeed(), player.askstoned())
                PLAYER_SHOTS += 1 # count all the shots of a player
                Fire = False # reset Fire Flag
            else: # tux can't fire, too much rockets are flying around...
                noammo_sound.play()
          
        if SmartBomb and player.alive():
            rockets = MAX_RAKETEN - len(raketen)
            rockets += 0.0   # transform rockets into a decimal 
            if rockets >= SMARTBOMBMIN: # at least 4 rockets aviable
                for r in range(int(rockets)):
                    rakete_sound.play()  # Smartbomb-sound ?
                    rakete = Rakete(SCREENRECT, player.askpos(),
                                  player.askdreh() + (r/rockets)*360,
                                  player.askspeed(), player.askstoned())
                    PLAYER_SHOTS += 1 # count all the shots of a player
                SmartBomb = False   
         
        #--- collision detection ---      
        # collision aliens and rakete ? 
            #--- aliens and rocket
        for rakete in pygame.sprite.groupcollide(raketen, aliens, False, False).keys():
            # False, True => kill Alien, kill rakete
            boom_sound.play()
            Explosion(rakete.askpos(),True)
            for alien in pygame.sprite.spritecollide(rakete, aliens, False):
                Explosion(alien.askpos())
                alien.kill()
                FRAGS += 1
                kills.setmsg(str(FRAGS))
                if rakete.askstoned() == True:
                    # no points because of peacefull hemp culture and lacking of focus
                    flyscore = FlyScore(rakete.askpos(),'+0')
                else:
                    SCORE = SCORE + 1
                    SCORE = SCORE + rakete.askbounce() # more points if rocket hit after bouncing from wall
                    if rakete.askbounce() > 0:
                        if HITMATRIX.has_key(rakete.askbounce()):
                            HITMATRIX[rakete.askbounce()]+=1
                        else:
                            HITMATRIX[rakete.askbounce()]=1   
                        cash_sound.play()   # sound for hitting after bouncing
                        flyscore = FlyScore(rakete.askpos(), '+' + str(rakete.askbounce()+1))
                        if rakete.askbounce() >= BOUNCE_KING: # king of bouncing
                            trommel_sound.play()
                    else:
                        HITMATRIX[0] += 1 # add a direct hit
                        flyscore = FlyScore(rakete.askpos(),'+1')
            rakete.kill()  
        scoreP1.setmsg(str(SCORE))
            
        # collision rakete and goodie ? 
        #--- rocket and goodie
        for rakete in pygame.sprite.groupcollide(raketen, goodies, False, False).keys():
            # what is that keys() good for ??
            Explosion(rakete.askpos(), True)
            goodie_shot_sound.play()
            for goodie in pygame.sprite.spritecollide(rakete, goodies, False):
                if goodie.asktext() == 'surprise':
                    # penalty for being ignorant 
                    flyscore = FlyScore(goodie.askpos(),'-1')
                    SCORE -= 1
                elif rakete.askstoned() == True  and goodie.asktext() == 'hemp':
                    # penalty for being a hemp-killer
                    SCORE -= 1
                    flyscore = FlyScore(goodie.askpos(),'-2')
                else:   
                    flyscore = FlyScore(goodie.askpos(),'0')
                goodie.kill()
            rakete.kill()     
        scoreP1.setmsg(str(SCORE))
        
         
        # collision smallsprite and aliens ?
        #--- smallsprite and aliens
        for alien in pygame.sprite.groupcollide(smallsprites, aliens, False, True): # don't know if .keys() is necessary or not
            for smallsprite in pygame.sprite.spritecollide(alien, smallsprites, 0):
                temppos = alien.askpos()
                alien.kill()
                Explosion(temppos)
                boom_sound.play()
                if player.askubuntu():
                    player.removeubuntu()
                if not player.askstoned(): # no points if Tux is stoned
                    FlyScore(temppos,'+1')
                    SCORE += 1 
                    scoreP1.setmsg(str(SCORE))
                else:
                    FlyScore(temppos, '0')    
                
        # collision player and aliens ?
        #--- player and aliens
        if (POST_MORTEM > 0) and (CHEAT == False): # only valid before the GAME OVER message...
            #bangbang = False 
            for alien in pygame.sprite.spritecollide(player, aliens, 0):
                if collision(player.askpos(), player.askdreh(), alien.askrect()) != 0:
                    #if colresult != 0:               # really a collision ?
                    # change: the smallsprites can destroy aliens, so that having ubuntu
                    # mode makes you no longer invulnerable.. you must steer carefull to 
                    # destroy the aliens with your ubuntu smallsprites (satelittes)
##                    if player.askubuntu():  # Tux survive because in ubuntu mode 
##                        boom_sound.play()
##                        Explosion(alien.askpos())
##                        player.removeubuntu()
##                        if not player.askstoned(): # no points if Tux is stoned
##                            FlyScore(alien.askpos(),'+1')
##                            SCORE += 1 
##                            scoreP1.setmsg(str(SCORE))
##                        else:
##                            FlyScore(alien.askpos(), '0')
##                        #FRAGS += 1 # no Frag for ubunut-style kamikaze killing
##                        #kills.setmsg(str(FRAGS))
##                        alien.kill()
##
##                    else:   # that was a collision, Tux is not in ubuntu-mode,  proceed to die
                        boom_sound.play()
                        Explosion(alien.askpos())
                        Explosion(player.askpos())
                        # FRAGS += 1     # suicide is not a frag, it is bad style
                        # SCORE = SCORE + 1
                        alien.kill()
                        STONED_SECS = player.asktotalstonedsec()
                        player.kill()
                        playerex_sound.play() # extra soundeffect for death player
                        GAME_OVER = True
                        PLAY_END = int(time.time())
                        PLAY_TIME = str((PLAY_END - PLAY_START)/3600) +":"+ time.ctime(PLAY_END - PLAY_START)[14:19]
                       
        #collision player and goodie ?
        #--- player and goodie
        if player.alive():      
            for goodie in pygame.sprite.spritecollide(player, goodies, 0):
                if goodie.asktext() == "hemp": # player get stoned and can't shoot strait anymore
                    SCORE += player.askserialhemp()
                    flyscore = FlyScore(goodie.askpos(), '+' + str(player.askserialhemp()))
                    scoreP1.setmsg(str(SCORE))
                    player.addhemp() 
                    status.setmsg("stoned")
                    goodie_pickup_sound.play()
                    goodie.kill()
                elif goodie.asktext() == "ubuntu": # player get protection by ubuntu
                    #flyscore = FlyScore(goodie.askpos(), "ubuntu protect you")
                    player.addubuntu()
                    #status2.setmsg("protected")
                    goodie_pickup_sound.play()
                    goodie.kill()
                elif goodie.asktext() == "wine":    # all enemys stay stupid around because Tux is masked
                    winetime0 = time.time() # the time of wine starts now
                    winetime = True # global Flag, asked by Aliens
                    goodie_pickup_sound.play()
                    goodie.kill()
                    for alien in aliens:
                        flyscore = FlyScore(alien.askpos(), '?') # the Aliens have no clue where Tux is now
                elif goodie.asktext() == "debian":  # the mighty debian destroy all enemys of Tux
                    goodie_pickup_sound.play()
                    goodie.kill()
                    for alien in aliens:
                        if SCREENRECT.collidepoint(alien.askpos()): # check if alien spawned in visible screenrect
                            LASERARRAY.append((time.time(),alien.askpos()))
                            boom_sound.play()
                            Explosion(alien.askpos())
                            if not player.askstoned():
                                flyscore = FlyScore(alien.askpos(), '+ 1')
                                SCORE += 1
                                scoreP1.setmsg(str(SCORE))
                            alien.kill()
                        
                        
        #collision player and (old) rocket ?
        #--- player and old rocket
        if player.alive():
            for rakete in pygame.sprite.spritecollide(player, raketen, False):
                if rakete.askageR() > ROCKET_TUXSAFETIME_SEC:
                    # really a collision ?
                    colresult = collision(player.askpos(),player.askdreh(),rakete.askrect())
                    if colresult != 0:
                        SCORE -= rakete.askbounce()*colresult  # punish for self - shooting, twice for head-hit
                        if colresult == 2: # self-headschot
                            FlyScore(rakete.askpos(), 'Headshot ! ' + str(rakete.askbounce()*-1*2))
                        else: # self-bellyshot
                            FlyScore(rakete.askpos(), str(rakete.askbounce()*-1))
                        scoreP1.setmsg(str(SCORE))
                        self_shot.play() # funny sound for being an idiot
                        Explosion(rakete.askpos(),True)
                        rakete.kill()
                
        # Death Animation: There is a bit of 'life' after death of Tux
        #--- Death and TopTen
        if GAME_OVER:
            #load_music('Runaway_Fashion-cj.mp3')
            POST_MORTEM -= 1 # decrease counter so that last explosion can be shown
            if POST_MORTEM <= 0: # now comes the GAME-OVER Screen
                if PLAYER_SHOTS == 0:
                    QUOTA = 0
                else:
                    QUOTA = round((FRAGS/(PLAYER_SHOTS+0.00))*100,1)
                if int(PLAY_END - PLAY_START) == 0:
                    STONEDQUOTA = 0
                else:
                    STONEDQUOTA = round((STONED_SECS / int(PLAY_END - PLAY_START))*100,1)
                #if len(HIGHSCORE) >= 9 and SCORE >= HIxxxx:   
                myname = ""
                if SCORE > HIGHSCORE[-1][0]:
                    #myname = ask(screen, 'Enter your name')
                    myname = ask(SCREENRECT, screen, 'Enter your name')
                    HIGHSCORE.append((SCORE, QUOTA, PLAY_TIME, STONEDQUOTA, myname)) # append adds the tuple to the list
                    HIGHSCORE.sort(reverse=True) # sort descending score
                    if len(HIGHSCORE) > 10:        # only top-ten list
                        HIGHSCORE = HIGHSCORE[:10] # a list start with item 0 
                    try:                         # write the new highscorelist
                        f = file('topten.txt','w')
                        for score, quota, playtime, stonedquota, name in HIGHSCORE:
                            line = str(score) + ',' + str(quota) + ',' + playtime + ',' + str(stonedquota) +','+name + '\n'
                            f.write(line)
                        f.close()
                    except:
                        print 'Could not write the file "topten.txt". You can play, but nobody will remember how good you play.'
                # game over text
                bigText(screen, background, SCREENRECT,
                      "GAME OVER (ESC = menu, q = play again)", 32, .1, False)
                bigText(screen, background, SCREENRECT,
                      "lifetime wasted playing this game (h:mm:ss) : " + PLAY_TIME,28,.15,False)
                if PLAYER_SHOTS == 0:
                    msg = "Shots: 0 / Kills: 0 / HitQuota: 0 Percent"
                else:
                    COMMENT = ""
                    if QUOTA == 100:
                        COMMENT = 'Perfect!'
                    elif QUOTA >= 90:
                        COMMENT = 'Good'
                    elif QUOTA >= 75:
                        COMMENT = 'o.k.'
                    elif QUOTA >= 50:
                        COMMENT = 'tolerable'
                    elif QUOTA >= 25:
                        COMMENT = 'bad'
                    else:
                        COMMENT = 'terrible'
                    msg = "Shots: %d / Kills: %d / HitQuota: %d %% ... that is %s " % (PLAYER_SHOTS, FRAGS, QUOTA, COMMENT )
                bigText(screen, background, SCREENRECT,
                      msg, 28, .2, False)
                #bigText(COMMENT, 36, .25, False)
                yoff = 0 
                if FRAGS > 0:
                    bigText(screen, background, SCREENRECT,
                         "Bounce / Value / Times / Score", 28,.3, False)
                    y = .33                 
                    for reflects, hits in HITMATRIX.items():                     
                        TableText(screen, background, SCREENRECT,
                               str(reflects).rjust(2), 20, y, yoff, -120)
                        TableText(screen, background, SCREENRECT,
                               str(reflects + 1).rjust(2), 20, y, yoff, -30)
                        TableText(screen, background, SCREENRECT,
                               str(hits).rjust(3), 20, y, yoff, 40)
                        TableText(screen, background, SCREENRECT,
                               str((reflects +1) * hits).rjust(3),20,y,yoff,120)
                        yoff += 22
                # Highscore-Liste
                TableText(screen, background, SCREENRECT,
                        'Rank',20,.35,yoff, -220, 'right')
                TableText(screen, background, SCREENRECT,
                        'Score',20,.35,yoff,-150, 'right')
                TableText(screen, background, SCREENRECT,
                        'Hitq.',20,.35,yoff,-70, 'right')
                TableText(screen, background, SCREENRECT,
                        'Time',20,.35,yoff,20, 'right')
                TableText(screen, background, SCREENRECT,
                        'Stoned',20,.35,yoff, 130, 'right')
                TableText(screen, background, SCREENRECT,
                        'Name',20,.35,yoff,170, 'left')
                rank = 1
                myrank = 0
                yoff += 12
                for score, quota, tim, stonedquota, name in HIGHSCORE:
                    yoff += 22
                    TableText(screen, background, SCREENRECT,
                            str(rank) + '. ', 20,.35,yoff, -220, 'right')
                    TableText(screen, background, SCREENRECT,
                            str(score),20,.35,yoff,-150,'right')
                    TableText(screen, background, SCREENRECT,
                            str(round(quota,1)) + ' %',20,.35,yoff, -70, 'right')
                    TableText(screen, background, SCREENRECT,
                            str(tim),20,.35,yoff,20,'right')
                    TableText(screen, background, SCREENRECT,
                            str(round(stonedquota, 1)) + ' %',20,.35, yoff, 130, 'right')
                    TableText(screen, background, SCREENRECT,
                            name, 20, .35, yoff, 170, 'left')
                    if name == myname and score == SCORE and tim==PLAY_TIME:
                        myrank = rank
                        # red rec around myrank
                        pygame.draw.rect(background, [255,0,0], (40,SCREENRECT.height* .35 + yoff - 12, SCREENRECT.width-80,24),2)
                        for babytux in range(1, (12-myrank)):
                            # 10 Tuxys for first rank, 9 Tuxys for second..
                            slice = int((SCREENRECT.width - 80) / (11-myrank))
                            xpos = 40
                            if babytux > 1:
                                xpos += slice * (babytux - 1)
                            xpos0 = xpos
                            xpos += random.randint(1,slice) 
                            #BabyTux( startpos, xmin, xmax, redline, SCREENRECT)...
                            BabyTux((xpos,random.randint(-250,-20)), xpos0, xpos0 + slice, SCREENRECT.height * .35 +yoff - 12, SCREENRECT)
                    rank += 1
                    #msg = str(rank).rjust(2) + '.:'+str(score).rjust(7) + ' / '  + str(ti) + ' / ' + name
                    #bigText(msg, 32, .35, False, False, yoff)
                msg = "Score: %d / biggest Wave: %d  Enemys " % (SCORE, MAX_ALIENS)
                if myrank != 0:
                    msg += " / Rank: " +str(myrank) + '.'
                bigText(screen, background, SCREENRECT,
                    msg, 28, .25, False)
                GAME_OVER = False # ahahaHAHAHARRR ! Immorrtaly exist !!
                #bigText("(press ESC or q to quit)", 36, .95, True)
                pygame.display.flip()
                #pygame.mixer.music.play() #'plays the funky music once
                #print "..." + Playername
                
        # thinking if a new alien shall be born
        
        if (len(aliens) < MAX_ALIENS) and (POST_MORTEM >0) and winetime == False:   # only if player is alive
            if len(aliens) == 0:
                MAX_ALIENS += 1  # let ther be more aliens because player killed all                
                Alien(SCREENRECT) # let a new alien be born !
            else:
                if alienreload > 0: # there was already a spawn short before now
                    alienreload -= 1 # subtract 1 from alienreload
                elif not int(random.random() * ALIEN_ODDS):
                    # really complicate math, i did not understand it fully myself
                    # if the term in the paranteses equal 0, a new alien will spawn
                    Alien(SCREENRECT)
                    alienreload = ALIEN_RELOAD # new safe time before new alien can spawn again
                    
          
        # difficulty
        # player can shoot twice as many bullets as enemys exist if ..RATIO = 2
        # player can always shoot at least one bullet
        LEN_ALIENS = len(aliens)
        MAX_RAKETEN = int(LEN_ALIENS * SHOTS_TO_ALIENS_RATIO) or 1 # this term is always at minimum 1
        LEN_RAKETEN = len(raketen)
        LEN_GOODIES = len(goodies)

        # new Goddie ?
        if time.time() - GOODIETIME > GOODIE_THINKABOUT: # time to think about a new Goodie
            GOODIETIME = time.time() # reset Goodietime
            if LEN_GOODIES < GOODIE_MAXLEN:  #no more then 2 Goodies at the same time
                if random.random() > GOODIE_CHANCEOFNEW:
                    goodie = Goodie(SCREENRECT) # new goodie shall be born
        # winetime ?
        if winetime == True:
            if time.time() - winetime0 > FLYSCOREMAXAGE_SEC:
                winetime = False #winetime is over
        # A.I.
        if POST_MORTEM > 0 and AI=="SEEK":  # only valid if player is alive and AI is clever
            PLAYER_X = player.askpos()[0]
            PLAYER_Y = player.askpos()[1]
        else:                              # let wander around the aliens on GAME OVER Screen   
            PLAYER_X = random.randint(0,SCREENRECT.width)
            PLAYER_Y = random.randint(0,SCREENRECT.height)

        #--- update Ui ---
        if player.alive():
            maxEnemys.setmsg(str(MAX_ALIENS))
            # max(0,x) to avoid negative vlaue of x
            ammo.setmsg(str(max(0,MAX_RAKETEN - LEN_RAKETEN)) + " / " + str(MAX_RAKETEN))
            player.setMaxLenRaketen(MAX_RAKETEN - LEN_RAKETEN)
            #if player.askubuntu() == False:
                #status2.setmsg("mortal")
            
                
            if player.askstoned() == False:
                status.setmsg("clean")
            else:
                # stonedtimer
                howmuch = player.askactualstonedpercent()  # 0 to 1, but beginning at midtop
                arctimer(screen, arccolor, arcrect, howmuch, polycolor)
            if player.askubuntu() == True:
                howmuch = player.askubuntupercent() # 0 to 1
                arctimer(screen, ucolor, urect, howmuch, polycolor)
        # sprites:  
        dirty = all.draw(screen) # dirty gives back a rect-list
        # dirty means that the dirty part of the screen needs redrawing.
        #--- laser beams ---
        # control laserrarray, paint beams
        sz = 0
        lminx = player.askpos()[0]
        lminy = player.askpos()[1]
        lmaxx = player.askpos()[0]
        lmaxy = player.askpos()[1]
        dirty.extend(laserdirty)  # neu
        laserdirty = [] # neu
        #SCREENREPAINT = False
        #have to save a Laser-dirtyrec for each laser beam. rec should grow, never shrink, to avoid artifacts.
        for beamtime, alienpos in LASERARRAY:
            # the Rect format is x_topleft, y_topleft, width, height) have to calculate clean rects from playerpos and alienpos
            #dirty.append(Rect(min(player.askpos()[0], alienpos[0]),min(player.askpos()[1],alienpos[1]),abs(player.askpos()[0]-alienpos[0])+1,abs(player.askpos()[1]-alienpos[1])+1))
            # min - 1 and max + 1 to make the rec always bigger than the beam
            laserdirty.append(Rect(min(player.askpos()[0], alienpos[0])-2,min(player.askpos()[1],alienpos[1])-2,abs(player.askpos()[0]-alienpos[0])+4,abs(player.askpos()[1]-alienpos[1])+4))
            if beamtime < time.time() - DEBIANRAYTIME:
                del LASERARRAY[sz]
            else:
                pygame.draw.line(screen, (random.randint(0,255), random.randint(0,255), random.randint(0,255)), player.askpos(), alienpos, 1) # was 255, 100, 150
            sz += 1
        dirty.extend(laserdirty) 
               
        if len(LASERARRAY) == 0 and LASERLENOLD != 0:
            # refresh the whole screen to avoid leftovers from DebianLaser (this happens sometimes)
            #print "totalrefresh"
            LASERLENOLD = 0
            #dirty = SCREENRECT
        else:
            LASERLENOLD = len(LASERARRAY)
            dirty.extend(dirtystars)
            dirty.append(Rect(arcrect.topleft[0] - 2, arcrect.topleft[1] - 2, arcrect.width + 4, arcrect.height + 4)) # the stoned-timer-arc - append always to clean after use
            dirty.append(Rect(urect.topleft[0] - 2, urect.topleft[1] - 2, urect.width + 4, urect.height + 4)) # the ubuntu-timer-arc - append always to clean after use
            
        pygame.display.update(dirty) # update of all 'dirty' rectangles
        
        
        # --end of main loop -- 

#--- main function
#this calls the 'main' function (in this case, the startgame()-function) when this script is executed
if __name__ == '__main__':
   startmenu(1024, 768) 
