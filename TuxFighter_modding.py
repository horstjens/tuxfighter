#***************************************
#*** Welcome to TuxFighter_modding ****
#***************************************
#This is a real python module, please make a backup before messing around
#all text behind a "#" is a comment 
#please don't forget the decimal point if it was present before. Some
#values are defined as decimals, and some others are defined as integers (see comments)
#if you want to change a decimal value from 2.9 to 3 change it to 3.0 !
# gpl, Horst JENS 2/2006
#---------------------------
# angle 'dreh' for Tux Sprite:
# 0 faces north (up)
# 90 faces west (left)
# 180 faces south (down)
# 270 faces east (right)
# ---------------------------------

#--- constant Values -----
EARTHACCEL = 0.07 # the earth-acceleration for BabyTuxys was 0.05
MAXFPS   = 60  # only whole numbers ! This is the max. allowed Frames per Second rate. Set to 0 for no limiting the framerate
ALIEN_SLOW = 1 # only whole numbers !
ALIEN_FAST = 1 # only whole numbers !
ALIEN_VERYFAST = 2 # only whole numbers !
ALIEN_IMAGETIME = 1.0 # time in sec for alien to loop throug all alien images
ALIEN_THINKTIME = 2.0 # time in sec the alien AI calculate new direction to move
ALIEN_BORNTIME = 2.5  # time in sec before alien AI start thinking new directions
BABYTUX_IMAGETIME = .22 # time in sec for BabyTux to loop throug all images
GOODIE_FAKTOR = 1  # only whole numbers !
GOODIE_SURPRISETIME_SEC = 1.5 # time in sec Goodie stays a surpriese (question marks)
GOODIE_LIFETIME_SEC = 6.0 # Goodie lifetimes in sec
GOODIE_MAXLEN = 2 # only whole numbers ! maximum number of Goodies present on the screen on the same time
#GOODIE_REBORN = 0.999  # random() must draw a greater number to restart a Goodie
GOODIE_THINKABOUT = 10.0 # time in sec when game think about spawning a new goodie
GOODIE_CHANCEOFNEW = .1 # (1.0 = always, 0.0 = never) Probatility that thinking about a Goodie leads to a new Goodie 
BABYTUX_IDLETIME = .23   # Time in sec a BabyTux sit around idle
TUX_SLOW = 2 # only whole numbers ! The normal speed of Tux
TUX_FAST = 4 # only whole numbers ! The fast-forwad speed of Tux if he is 'running'
TUX_RADIUS = 54 # The lenght of the Radius of a Circle build around Tux in Pixel
TUX_DEFAULTUBUNTUS = 3 # only whole numbers ! How many ubuntus (=Extra lives for Tux) add each ubuntu logo.
TUX_BELLYCENTER = -14 # only whole numbers ! How many pixel the bellycenter is under the tuxcenter
TUX_BELLYRADIUS = 29 # only whole numbers ! radius length of bellycircle in pixel
TUX_HEADCENTER = 27 # only whole numbers ! How many pixel the headcenter is over the tuxcenter
TUX_HEADRADIUS = 14 # only whole numbers ! radius lenght of headcircle in pixel
TUX_CONTROLANGLE = 15 # only whole numbers ! for collision-detection: a circle (head, belly) is tested at every >15< GRAD for a Collision. lower value gives more precision at collision detection, but makes game slower
TUX_NEWBUBBLE = 0.4 # must be between 0.0 and 1.0, chance per frame for a new bubble. Lower this value if game is too slow
ROCKET_NEWBUBBLE = 0.22 # must be between 0.0 and 1.0,  chance per frame for a new bubble. Lower this value if game is too slow
ROTATINGARC = 15    # only whole numbers ! must be between 0 and 360. Is the arc of bubbles leaving Tux while he is rotating
ROCKET_SPEED = 3.0 # how fast a rocket moves in pixels/frame
ROCKET_BOUNCE = 0.7 # 0 -> never bounce, 1.0 -> always bounce
ROCKET_STONEDIRCHANGETIME = 0.5 # time in sec a 'stoned' rocket will init a new directionchange
ROCKET_STONEDDELTARANGE = 2.0  # range of per stoned Frame direction change ( - half of it)
ROCKET_STONEDDELTARANGE2 =  .15 # range of per stoned Frame speed change ( - half of it)
ROCKET_TUXSAFETIME_SEC = 1.5 # time in sec a Rocket is "save" for the Player
ROCKET_STONEDFACTORFACTOR = .99 # every frame the initial-speed of the stoned rocket is multiplied by this.
PLAYER_ROTATION_SPEED = 2.8 # how much degree the player can turn per frame 
PLAYER_ROTATION_SPEED_SLOW = 1.5 # how musch degree per frame player can turn if not moving ?
EXPLOTIME = 1.0 # (.33) time in sec how long a explosion stays visible
EXPLOCYCLE = .066 # time in sec a single explosion image stays visible
SMARTBOMBMIN = 4 # this number of rockets must be aviable to do a smartbomb with 'b'
#STONED_MAX = 1200 # max stoned time in frames (60 Frames/second)
STONED_MAX_SEC = 20.0 # time in sec of being stoned
UBUNTU_MAX_SEC = 15.0 # time in sec of being protected by ubuntu
NUMSTARS = 100
STARSMINVELX = 0.3
STARSMINVELY = 0.6
FLYSCOREMAXAGE_SEC = 2.0 # Max Age in sec for flying Score
DEBIANRAYTIME = 2.0 # time in sec a debian ray of death stays visible (was 1)

SLOWCOLOR = 92,92,92 # all colors have a R(ed) G(reen) B(lue) Value between 0 and 255
#fastcolor = Color('red')
FASTCOLOR = 255, 0, 0
ROCKETCOLOR = 200,80,80
ROTATINGCOLOR = 0,0,200 # blue
#stonedcolor = Color('green')
#STONEDCOLOR = 0,200,0
#STONEDCOLOR2 = 50,255,0