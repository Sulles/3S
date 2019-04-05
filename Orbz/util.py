import math

FPS = 30
SURF_WIDTH = 600
SURF_HEIGHT = 400
LINE_LENGTHS = 25
MAX_EMEMS_SHOWN = 100
RAD_GROWTH_RATE = 5
ToDeg = 180/math.pi
ToRad = math.pi/180

LIGHTGRAY= (175, 175, 175)
GRAY     = (100, 100, 100)
DARKGRAY = ( 50,  50,  50)
BLACK    = (  0,   0,   0)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
WHITERED = (255, 230, 230)
RED      = (255,   0,   0)
PALERED  = (255,  75,  75)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
PALEBLUE = ( 75,  75, 255)
YELLOW   = (255, 255,   0)
PALEYELLOW=(255, 255, 175)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
PHOBOSCLR= (222, 184, 135)
DEIMOSCLR= (255, 222, 173)
BROWN    = (255, 240, 220)
DARKBROWN= (200, 190, 170)
DARKBLUE = ( 75,  75, 255)
BGCOLOR  = (  0,   0,	0)


def color2array(color):
    arry = [color[0], color[1], color[2]]
    return arry


def object_pos_to_screen(middle_point, array=True):
    if array:
        return [int(middle_point[0] + SURF_WIDTH/2), int(SURF_HEIGHT/2 - middle_point[1])]
    else:
        return (int(middle_point[0] + SURF_WIDTH/2), int(SURF_HEIGHT/2 - middle_point[1]))