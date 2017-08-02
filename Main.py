#!/usr/bin/env python
# SOLAR SYSTEM SIMULATOR

import pygame, math, sys, os
import numpy as np
from pygame.locals import *
from system import *
from BackEndData import *


##################################################################################
############# MAIN PROGRAM ##############
#########################################

# ==================================================
# MAIN METHOD
# Handles:
#   - FPS
#   - Display Window Params
#   - Calling Initialiation Method
#   - Calling Pysics Engine
#   - Calling GUI
#   - Calling Renderer
#   - Refreshing Display Window
def main():
	global FPSCLOCK, DISPLAYSURF
	TIME_SCALAR = 1
	ACTUAL_SCALAR = 0
	GOD_LOOP = int(1)
	BASIC_LOOP = int(FPS+1)
	BASIC_LOOP_COUNTER = int(1)
	FPSCLOCK = pygame.time.Clock()
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((SURF_WIDTH, SURF_HEIGHT))
	pygame.display.set_caption('Solar System Simulator')

	# INITIALIZE ALL BODIES
	initialize_bodies()
	
	# FOCUS ON FIRST ROOT
	FocusBody = ALL_BODIES.getRoots()[0]
	PREV_MAP_INDEX = []
	MAP_INDEX = 0
	siblings = ALL_BODIES.getRoots()

	SOI = True

	KM2PIX = np.array([1./1000], dtype = np.float64)
	
	# GAME LOOP
	while True:
		START_UPS_TIC = FPSCLOCK.get_time()
		
		# GAME EVENTS
		for event in pygame.event.get():
			# EXIT CONDITION
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				
			# KEY INPUT LOOP
			elif event.type == KEYDOWN:
				
			   ## ZOOM INPUT ##
				if event.key == K_SLASH:
					# ZOOM IN
					KM2PIX = zoomIn(KM2PIX)
				elif event.key == K_PERIOD:
					# ZOOM OUT
					KM2PIX = zoomOut(KM2PIX)
					
				## TIME_SCALAR KEY INPUT ##
				elif event.key == K_RIGHTBRACKET:
					if BASIC_LOOP > 1:
						BASIC_LOOP -= 10
					elif TIME_SCALAR < 10000:
						TIME_SCALAR *= 10
					else: 
						GOD_LOOP *= 2
				elif event.key == K_LEFTBRACKET:
					if GOD_LOOP > 1:
						GOD_LOOP = int(GOD_LOOP/2)
					elif TIME_SCALAR > 1:
						TIME_SCALAR = int(TIME_SCALAR/10)
					elif BASIC_LOOP < FPS:
						BASIC_LOOP += 10


				## MAP / FOCUS KEY INPUT ##
				# KEY UP            
				if event.key == K_UP:
					if FocusBody.getParent():
						# ZOOM OUT
						KM2PIX = zoomOut(KM2PIX)
						# UPDATE MAP AND INDEX
						MAP_INDEX = PREV_MAP_INDEX[-1]
						FocusBody = FocusBody.getParent()
						if not FocusBody.getParent():
							siblings = (ALL_BODIES.getRoots())
							PREV_MAP_INDEX = []
						else:
							siblings = [FocusBody.getParent()] + FocusBody.getParent().getChildren()
							PREV_MAP_INDEX.pop()
				# KEY DOWN
				elif event.key == K_DOWN:
					if len(FocusBody.getChildren()) > 0:
						# ZOOM IN
						KM2PIX = zoomIn(KM2PIX)
						# UPDATE MAP AND INDEX
						PREV_MAP_INDEX.append(MAP_INDEX)
						MAP_INDEX = 1
						FocusBody = FocusBody.getChildren()[0]
						if not FocusBody.getParent():
							siblings = (ALL_BODIES.getRoots())
						else:
							siblings = [FocusBody.getParent()] + FocusBody.getParent().getChildren()

				# KEY RIGHT
				elif event.key == K_RIGHT:
					MAP_INDEX = (MAP_INDEX+1)%len(siblings)
					FocusBody = siblings[MAP_INDEX]

				# KEY LEFT
				elif event.key == K_LEFT:
					MAP_INDEX = (MAP_INDEX-1)%len(siblings)
					FocusBody = siblings[MAP_INDEX]



		### RUNNING PHYSICS ENGINE ###
		# LINEAR SCALE
		if ACTUAL_SCALAR != TIME_SCALAR:
			if ACTUAL_SCALAR == 0 and TIME_SCALAR == 1:
				PhysicsEngine(TIME_SCALAR)
			elif ACTUAL_SCALAR > TIME_SCALAR:
				ACTUAL_SCALAR -= 5
			else:
				ACTUAL_SCALAR += 5
			PhysicsEngine(ACTUAL_SCALAR)
			
		# BASIC LOOP, FOR WHEN SIM IS BETWEEN 1SEC AND 60SEC
		elif BASIC_LOOP > 1 and BASIC_LOOP_COUNTER >= 1 and GOD_LOOP == 1:
			if BASIC_LOOP_COUNTER == BASIC_LOOP:
				PhysicsEngine(TIME_SCALAR)
			elif BASIC_LOOP_COUNTER == 60:
				BASIC_LOOP_COUNTER = 1
			else:
				BASIC_LOOP_COUNTER += 1

		# GOD MODE
		elif GOD_LOOP > 1:
			for x in range(0, GOD_LOOP):
				PhysicsEngine(TIME_SCALAR)
		
		else:
			PhysicsEngine(TIME_SCALAR)
		
		
		# FOCUS ON...
		Focus = FocusBody.Position

		# RENDERING OBJECTS
		DISPLAYSURF.fill(BGCOLOR)
		Renderer(KM2PIX[0], Focus, SOI)
		Sim_Speed = TIME_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP) if ACTUAL_SCALAR == 0 else ACTUAL_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP)
		GUI(Sim_Speed, FocusBody, KM2PIX[0], FPSCLOCK, START_UPS_TIC, siblings)
		pygame.display.update()
		
		# IF NOT GOING THROUGH THE LINEAR SCALE, STICK TO 60 FPS LIMIT
		if ACTUAL_SCALAR == TIME_SCALAR or ACTUAL_SCALAR == 0:
			FPSCLOCK.tick(FPS)



# ==================================================
# GUI
# Handles:
#   - Displaying list of bodies in system
#   - Displaying current focus point
#   - Displaying TIME_SCALAR
def GUI(Sim_Speed, FocusBody, KM2PIX, FPSCLOCK, START_UPS_TIC, siblings):
	# SETTING UP FONT
	path = os.path.abspath('resources/fonts/Cubellan.ttf')
	BasicFont = pygame.font.Font(path, 12)

	### INFORMATION GUI TOP LEFT ###
	# BACKGROUND
	global BGCOLOR
	pygame.draw.rect(DISPLAYSURF, GUI_COLOR, (10, 10, 120, 54), 0)
	pygame.draw.rect(DISPLAYSURF, FONT_COLOR, (7, 7, 126, 60), 1)
	pygame.draw.rect(DISPLAYSURF, FONT_COLOR, (4, 4, 132, 66), 1)

	# FOCUSED ON... TEXT
	temp = 'Focus - %s' %FocusBody.Name
	FocusText = BasicFont.render(temp, True, FONT_COLOR)
	DISPLAYSURF.blit(FocusText, (12,12))

	# SIM SPEED TEXT
	temp = 'SimSpeed %s' %Sim_Speed
	SimSpeedText = BasicFont.render(temp, True, FONT_COLOR)
	DISPLAYSURF.blit(SimSpeedText, (12, 24))

	# KM2PIX TEXT
	temp = 'Scale: %s' %KM2PIX
	ScaleText = BasicFont.render(temp, True, FONT_COLOR)
	DISPLAYSURF.blit(ScaleText, (12, 36))

	# UPS/FPS DISPLAY TEXT
	if FPSCLOCK.get_time() > 0:
		#UPS = int(1000/FPSCLOCK.get_time())
		#temp = 'UPS: %s' %UPS
		FPS = int(FPSCLOCK.get_fps())
		temp = 'FPS: %s' %FPS
		Text = BasicFont.render(temp, True, FONT_COLOR)
		DISPLAYSURF.blit(Text, (12, 48))
	else:
		UPSText = BasicFont.render('TOO FAST', True, FONT_COLOR)
		DISPLAYSURF.blit(UPSText, (12, 48))


	# RETICLE
	radius = int((FocusBody.Diameter.round()*KM2PIX/2) + 5)
	pygame.draw.circle(DISPLAYSURF, FONT_COLOR, (int(round(SURF_WIDTH/2)), int(round(SURF_HEIGHT/2))), int(radius), 1)
	pygame.draw.polygon(DISPLAYSURF, FONT_COLOR, ((int(SURF_WIDTH/2) - 3, int(SURF_HEIGHT/2) - radius), (int(SURF_WIDTH/2), int(SURF_HEIGHT/2) - radius - 5), (int(SURF_WIDTH/2) + 3, int(SURF_HEIGHT/2) - radius)), 1)
	temp = FocusBody.Name
	text = BasicFont.render(temp, True, FONT_COLOR)
	textrect = text.get_rect()
	textrect.centerx = round(SURF_WIDTH/2)
	textrect.centery = round(SURF_HEIGHT/2) - radius - 12
	DISPLAYSURF.blit(text, textrect)

	# MAP
	mapDisplay(FocusBody, BasicFont, siblings)


# DISPLAYS A "MAP" OF SYSTEM
def mapDisplay(FocusBody, BasicFont, siblings):
	# COMPILE LIST OF TEXTS TO DISPLAY AND THEIR SPACE NEEDED TO DISPLAY
	l2pix = 5 #letter 2 pixel
	offset = 5
	LOWKEYCOLOR = clrs["GRAY"]
	topTexts = []
	topX = []
	topY = 10
	midTexts = []
	midX = []
	midY = 25
	lowTexts = []
	lowX = []
	lowY = 40

	# FIRST GETTING PARENT OR ROOTS OF SYSTEM
	if FocusBody.getParent() in ALL_BODIES.getRoots():
		for body in ALL_BODIES.getRoots():
			topTexts.append(BasicFont.render(body.Name, True, LOWKEYCOLOR))
			topX.append(len(body.Name)*l2pix)
	elif FocusBody.getParent():
		body = FocusBody.getParent()
		topTexts.append(BasicFont.render(body.Name, True, LOWKEYCOLOR))
		topX.append(len(body.Name)*l2pix)

	# NEXT GETTING OBJECT AND OBJECTS NEXT TO IT
	try:
		for body in siblings:
			if body == FocusBody:
				midTexts.append(BasicFont.render(body.Name, True, clrs["WHITE"]))
			else:
				midTexts.append(BasicFont.render(body.Name, True, LOWKEYCOLOR))
			midX.append(len(body.Name)*l2pix)
	except:
		midTexts.append(BasicFont.render(body.Name, True, clrs["WHITE"]))
	
	# LASTLY, GET ALL CHILDREN
	if FocusBody.getChildren() and FocusBody.Name != siblings[0].Name:
		for body in FocusBody.getChildren():
			lowTexts.append(BasicFont.render(body.Name, True, LOWKEYCOLOR))
			if len(FocusBody.getChildren()) > 1:
				lowX.append(len(body.Name)*l2pix)


	# NOW TO DISPLAY EVERYTHING
	# DISPLAY TOP
	if len(topTexts)>0:
		text = topTexts[0]
		textrect = topTexts[0].get_rect()
		textrect.centerx = SURF_WIDTH/2
		textrect.centery = topY
		DISPLAYSURF.blit(text, textrect)

	# DISPLAY MIDDLE
	X = SURF_WIDTH/2 - sum(midX)
	if len(midTexts) > 1:
		for x in range(0,len(midTexts)):
			text = midTexts[x]
			textrect = midTexts[x].get_rect()
			textrect.centerx = X + offset + midX[x]
			textrect.centery = midY
			DISPLAYSURF.blit(text, textrect)
			X += midX[x] + offset + midX[x]
	else:
		text = midTexts[0]
		textrect = text.get_rect()
		textrect.centerx = SURF_WIDTH/2
		textrect.centery = midY
		DISPLAYSURF.blit(text, textrect)

	# DISPLAY LOWER LEVEL
	X = SURF_WIDTH/2 - sum(lowX)
	if len(lowTexts) > 1:
		for x in range(0,len(lowTexts)):
			text = lowTexts[x]
			textrect = lowTexts[x].get_rect()
			textrect.centerx = X + offset + lowX[x]
			textrect.centery = lowY
			DISPLAYSURF.blit(text, textrect)
			X += lowX[x] + offset + lowX[x]
	elif len(lowTexts) > 0:
		text = lowTexts[0]
		textrect = text.get_rect()
		textrect.centerx = SURF_WIDTH/2
		textrect.centery = lowY
		DISPLAYSURF.blit(text,textrect)



# ==================================================
# RENDERER
# Handles:
#   - Iterating through all Stars, Planets, Moons and Calling Display Function
#   - Zoom
#   - Conversion of km to pixels
def Renderer(KM2PIX, Focus, SOI):

	for body in ALL_BODIES:
		display(body, KM2PIX, Focus, SOI)


# ==================================================
# PHYSICS ENGINE
# Handles:
#   - Updating Velocity and Position of All Stars, Planets, Moons
def PhysicsEngine(TIME_SCALAR):

	for bodyA in ALL_BODIES:

		# ONLY CALCULATE IF :
		#   - IT ORBITS PARENT
		#   - bodyB IS A STAR
		#   GOT RID OF -> IS ON SAME LEVEL AS OTHER CHILDREN <- REQUIREMENT, IS USELESS AND SOI PROVES IT
		for bodyB in ALL_BODIES:
			if bodyB != bodyA and (bodyB in ALL_BODIES.getRoots() or bodyB == bodyA.Parent):
				DistanceArray = bodyB.Position - bodyA.Position
				Distance = np.linalg.norm(bodyB.Position - bodyA.Position)
				angle = math.atan(DistanceArray[1]/DistanceArray[0])
				GForce = TIME_SCALAR*G*bodyB.Mass[0]/(Distance*Distance)
				if bodyA.Position[0] > bodyB.Position[0]:
					ForceX = -math.cos(angle)*GForce[0]
					ForceY = -math.sin(angle)*GForce[0]
				else:
					ForceX = math.cos(angle)*GForce[0]
					ForceY = math.sin(angle)*GForce[0]

				bodyA.Velocity = bodyA.Velocity + np.array([ForceX,ForceY])


	for body in ALL_BODIES:
		body.Position = body.Position + TIME_SCALAR*body.Velocity


# DISPLAY
def display(self, KM2PIX, Focus, SOI):
	MiddlePoint = KM2PIX*(self.Position - Focus)
	CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
	CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

	# ENABLING DISSAPPEARING PLANETS
	# pixelSize = KM2PIX*self.Diameter/2
	# if CheckXAxis and CheckYAxis and pixelSize > 0.5
	if CheckXAxis and CheckYAxis:
		pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*(self.Diameter.round()/2)), 0)
		
		if SOI and self.SOI != None and self.SOI*KM2PIX > 1 and self.SOI*KM2PIX < SURF_WIDTH:
			pygame.draw.circle(DISPLAYSURF, FONT_COLOR, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(self.SOI*KM2PIX), 1)


# HANDLE ZOOMING
def zoomIn(KM2PIX):
	if KM2PIX >= 1/10:
		KM2PIX *= 2
	else:
		KM2PIX *= 10
	return KM2PIX

def zoomOut(KM2PIX):
	if KM2PIX <= 1/10:
		KM2PIX /= 10
	else:
		KM2PIX /= 2
	return KM2PIX

 
# ==================================================
# INTIALIZATION METHOD
# Handles:
#   - Creating and Defining Stars, Planets, Moons
#   - Creating Callable lists of Stars, Planets, Moons
def initialize_bodies():
	print()
	print("List of Bodies Created...")

	global ALL_BODIES
	ALL_BODIES = System(os.path.abspath('resources/systems/solar.json'))



# CALLING THE PROGRAM
main()
