import numpy as np 

# COLOR DICTIONARY
clrs = dict(
	LIGHTGRAY= (175, 175, 175),
	GRAY     = (100, 100, 100),
	DARKGRAY = ( 50,  50,  50),
	BLACK    = (  0,   0,   0),
	NAVYBLUE = ( 60,  60, 100),
	WHITE    = (255, 255, 255),
	WHITERED = (255, 230, 230),
	RED      = (255,   0,   0),
	PALERED  = (255,  75,  75),
	GREEN    = (  0, 255,   0),
	BLUE     = (  0,   0, 255),
	PALEBLUE = ( 75,  75, 255),
	YELLOW   = (255, 255,   0),
	PALEYELLOW=(255, 255, 175),
	ORANGE   = (255, 128,   0),
	PURPLE   = (255,   0, 255),
	CYAN     = (  0, 255, 255),
	PHOBOSCLR= (222, 184, 135),
	DEIMOSCLR= (255, 222, 173),
	BROWN    = (255, 240, 220),
	DARKBROWN= (200, 190, 170),
	DARKBLUE = ( 75,  75, 255)
)

# CONSTANTS
FPS = 60
SURF_WIDTH = 1200
SURF_HEIGHT = 700
BGCOLOR = (0,0,0)
FONT_COLOR = (255,)*3
GUI_COLOR = clrs["DARKGRAY"]

# CONSTANTS
# 1Exagram = 10^18 Kg
# 1Kilometer = 10^3 m
G = np.array([6.67408*(10**-2)], dtype = np.float64)   # Km^3/(Eg*s^2)
AU = 1.496*(10**8)      # Km

NAMESPACE = {'G':G,  'AU':AU, "EARTH_DIA":12742, "EARTH_MASS":5.972*10**6, "SUN_MASS":1.989e12}
exec("import math", NAMESPACE)
NAMESPACE.update(clrs)