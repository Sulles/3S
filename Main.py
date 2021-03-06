#!/usr/bin/env python
# SOLAR SYSTEM SIMULATOR

# STARTUP
print('LOADING...')

import pygame, math, sys, os, random
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
	global FPSCLOCK, DISPLAYSURF, ENABLE_ELLIPSE_DRIVE, ALL_BODIES
	TIME_SCALAR = 1
	ACTUAL_SCALAR = 0
	GOD_LOOP = int(1)
	BASIC_LOOP = int(FPS+1)
	BASIC_LOOP_COUNTER = int(1)
	ENABLE_ELLIPSE_DRIVE = False
	FPSCLOCK = pygame.time.Clock()
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((SURF_WIDTH, SURF_HEIGHT))
	pygame.display.set_caption('Solar System Simulator')

	# SETTING UP FONT
	filename = 'Cubellan.ttf'
	path = resource_path(os.path.join('resources', filename))
	BasicFont = pygame.font.Font(path, 12)
	LargerBasicFont = pygame.font.Font(path, 16)

	# INITIALIZE ALL BODIES
	ALL_BODIES = initialize_bodies()

	# INITIALIZE PLAYER
	initPlayer()
	
	# FOCUS ON FIRST ROOT
	FocusBody = ALL_BODIES.getRoots()[0]
	PREV_MAP_INDEX = []
	MAP_INDEX = 0
	siblings = ALL_BODIES.getRoots()

	SOI = False

	KM2PIX = np.array([1./10000], dtype = np.float64)
	
	# GAME LOOP
	while True:
		START_UPS_TIC = FPSCLOCK.get_time()
		
		# GAME EVENTS
		for event in pygame.event.get():
			# EXIT CONDITION
			if event.type == QUIT:
				terminate()

				
			# KEY INPUT LOOP
			elif event.type == KEYDOWN:

				# OTHER EXIT CONDITION
				if (event.key == K_ESCAPE):
					terminate()
				
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
				# KEY W = UP           
				if event.key == K_w:
					if FocusBody.getParent():
						# ZOOM OUT
						#KM2PIX = zoomOut(KM2PIX)
						# UPDATE MAP AND INDEX
						if (PREV_MAP_INDEX):
							MAP_INDEX = PREV_MAP_INDEX[-1]
						else:
							MAP_INDEX = 1
						FocusBody = FocusBody.getParent()
						if not FocusBody.getParent():
							siblings = (ALL_BODIES.getRoots())
							PREV_MAP_INDEX = []
						else:
							siblings = [FocusBody.getParent()] + FocusBody.getParent().getChildren()
							if (PREV_MAP_INDEX):
								del PREV_MAP_INDEX[-1]

				# KEY S = DOWN
				elif event.key == K_s:
					if len(FocusBody.getChildren()) > 0:
						# ZOOM IN
						#KM2PIX = zoomIn(KM2PIX)
						# UPDATE MAP AND INDEX
						PREV_MAP_INDEX.append(MAP_INDEX)
						MAP_INDEX = 1
						FocusBody = FocusBody.getChildren()[0]
						if not FocusBody.getParent():
							siblings = (ALL_BODIES.getRoots())
						else:
							siblings = [FocusBody.getParent()] + FocusBody.getParent().getChildren()

				# KEY D = RIGHT
				elif event.key == K_d:
					MAP_INDEX = (MAP_INDEX+1)%len(siblings)
					FocusBody = siblings[MAP_INDEX]

				# KEY A = LEFT
				elif event.key == K_a:
					MAP_INDEX = (MAP_INDEX-1)%len(siblings)
					FocusBody = siblings[MAP_INDEX]

				# CHANGE FOCUS BETWEEN PLAYER AND OBJECTS(PLANETS)
				# ---------------- NEEDS TO BE FLESHED OUT FOR PROPER GUI DISPLAY
				elif event.key == K_p:
					if (len(siblings) > 0 and FocusBody == siblings[MAP_INDEX]):
						FocusBody = PLAYER_OBJECTS.getRoots()[0]
					else:
						FocusBody = siblings[MAP_INDEX]

				## PLAYER ACTIONS ##
				# ROTATE LEFT
				elif event.key == K_RIGHT:
					PLAYER_OBJECTS.getRoots()[0].changeAngle(-5)
				# ROTATE RIGHT
				elif event.key == K_LEFT:
					PLAYER_OBJECTS.getRoots()[0].changeAngle(5)
				# ADD THRUST
				elif event.key == K_UP:
					PLAYER_OBJECTS.getRoots()[0].changeThrust(0.01)	# THRUST IS IN KM/SS
					print(PLAYER_OBJECTS.getRoots()[0].Thrust)
				# DECREASE THRUST
				elif event.key == K_DOWN:
					if (PLAYER_OBJECTS.getRoots()[0].Thrust > 0):
						PLAYER_OBJECTS.getRoots()[0].changeThrust(-0.01)
					print(PLAYER_OBJECTS.getRoots()[0].Thrust)


				## ENABLING ELLIPSE DRIVE
				elif event.key == K_e:
					spoolEllipseDrive()
					#ENABLE_ELLIPSE_DRIVE = True
				## JUMP ELLIPSE DRIVE
				elif event.key == K_j:
					#ENABLE_ELLIPSE_DRIVE = True
					for body in ALL_BODIES:
						if (body != ALL_BODIES.getRoots()[0]):
							print(body.Name + " is jumping from angle: " + str(body.theta*TODEG))
							EllipseDrive(body, 10)
					#PhysicsEngine(10)
					#ENABLE_ELLIPSE_DRIVE = False
							




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
		Sim_Speed = TIME_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP) if ACTUAL_SCALAR == 0 else ACTUAL_SCALAR*GOD_LOOP*(FPS+2-BASIC_LOOP) # WTF ACTUALLY HAPPENED HERE
		GUI(Sim_Speed, FocusBody, KM2PIX[0], FPSCLOCK, START_UPS_TIC, siblings, BasicFont, LargerBasicFont)

		# UPDATE DISPLAY
		pygame.display.update()
		
		# IF NOT GOING THROUGH THE LINEAR SCALE, STICK TO 60 FPS LIMIT
		if ACTUAL_SCALAR == TIME_SCALAR or ACTUAL_SCALAR == 0:
			FPSCLOCK.tick(FPS)



# ==================================================
# Spooling the Ellipse Drive :
# 	- Run the physics engine a few times and enable position 2 past accumulation
# 	- Calculate dA/dt, necessary for the Ellipse Drive
def spoolEllipseDrive():
	print(); print("Preparing Bodies for Ellipse Drive...")
	# Spool steps times, the larger the number, the better the end results should be...
	steps  = 100
	TotalAnalysisTime = 1000			# keep TotalAnalysisTime large to avoid 0 area triangles
	stepSize = int(TotalAnalysisTime/steps)
	for x in range(0, TotalAnalysisTime, stepSize):
		PhysicsEngine(stepSize)
		for body in ALL_BODIES:
			body.addPos2Past()
	for body in ALL_BODIES:
		if (body.e_ != None):
			body.calculateEllipse(TotalAnalysisTime, stepSize)
		else:
			print("WARNING: " + str(body.Name) + " will not participate in the Ellipse Drive")

	print(); print("ELLIPSE DRIVE READY"); print()



# ==================================================
# GUI
# Handles:
#   - Displaying list of bodies in system
#   - Displaying current focus point
#   - Displaying TIME_SCALAR
def GUI(Sim_Speed, FocusBody, KM2PIX, FPSCLOCK, START_UPS_TIC, siblings, BasicFont, LargerBasicFont):

	### INFORMATION GUI TOP LEFT ###
	# BACKGROUND
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
	temp = 'Scale: %s' %np.round(KM2PIX,10)
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


	# INSTRUCTION TEXT (English)
	instruction_texts = [	'WASD keys to change between objects',
							'P to zoom directly to player'
							'Arrow keys to rotate player',
							'Zoom In  . (period)',
							'Zoom Out  / (forward slash)',
							'Speed Up  ] (right bracket)',
							'Speed Down  [ (left bracsket)']
	for x in range(0, len(instruction_texts)):
		txt = LargerBasicFont.render(instruction_texts[x], True, FONT_COLOR)
		DISPLAYSURF.blit(txt, (11, SURF_HEIGHT/6 + (x*20)))


	# RETICLE
	radius = int((FocusBody.Diameter.round()*KM2PIX/2) + 5)
	pygame.draw.circle(DISPLAYSURF, FONT_COLOR, (int(SURF_WIDTH/2), int(SURF_HEIGHT/2)), int(radius), 1)
	pygame.draw.polygon(DISPLAYSURF, FONT_COLOR, ((int(SURF_WIDTH/2) - 3, int(SURF_HEIGHT/2) - radius), (int(SURF_WIDTH/2), int(SURF_HEIGHT/2) - radius - 5), (int(SURF_WIDTH/2) + 3, int(SURF_HEIGHT/2) - radius)), 1)
	temp = FocusBody.Name
	text = BasicFont.render(temp, True, FONT_COLOR)
	textrect = text.get_rect()
	textrect.centerx = round(SURF_WIDTH/2)
	textrect.centery = round(SURF_HEIGHT/2) - radius - 12
	DISPLAYSURF.blit(text, textrect)

	# MAP DISPLAY
	mapDisplay(FocusBody, BasicFont, siblings)




# ==================================================
# PHYSICS ENGINE
# Handles:
#   - NBody Calculations
#	- Ellipse Drive
def PhysicsEngine(TIME_SCALAR):
	for body in ALL_BODIES:
		if ENABLE_ELLIPSE_DRIVE and body.e_ != None:
			# RUN ELLIPSE DRIVE FOR ALL BODIES THAT HAVE IT
			if (TIME_SCALAR <= 1):
				print("ERROR: Time Scalar too low for Ellipse Drive")
				ClassicalPhysicsEngine(body, TIME_SCALAR)
			else:
				currentTheta = getTheta(body.Position, body.Parent.Position)
				print(currentTheta*TODEG)
				EllipseDrive(body, TIME_SCALAR, currentTheta)
		else:
			# RUN NBODY CALCULATIONS
			ClassicalPhysicsEngine(body, TIME_SCALAR)

		#if (body.Name == "Phobos"):
		#	print(getTheta(body.Position, body.Parent.Position)*TODEG)

	# RUN PHYSICS ENGINE FOR PLAYERS
	PlayerPhysicsEngine(TIME_SCALAR)

	## PUSH NEW POSITIONS
	for body in ALL_BODIES:
		body.Position += TIME_SCALAR*body.Velocity
		if (body.Parent != None):
			body.recalcTheta()
	for player in PLAYER_OBJECTS:
		player.Position += TIME_SCALAR*player.Velocity


def EllipseDrive(self, dt):
    print(str(self.Name) + " jumping from " + str(self.theta*ToDeg)) # + " to...")
    old_r = np.linalg.norm(self.Position - self.Parent.Position)
    dTheta = self.a*self.b*self.n*dt/(old_r*old_r)
    self.theta -= dTheta
    if (self.theta > 2*math.pi):
        self.theta -= 2*math.pi
    if (self.CircularOrbit):
        r = self.a
    else:
        r = (self.a*(1-self.e_*self.e_))/(1+self.e_*math.cos(self.theta))
    pos = np.array([r*math.cos(self.theta), r*math.sin(self.theta)], dtype = np.float64) + self.Parent.Position
    self.Position = self.format64(self.rotatePoint(self.Parent.Position, pos, self.angle)) #rotatePoint(self.getBarycenter(), pos, self.angle)
    self.Acceleration = self.format64(vecSub(self.Velocity, self.PastVel)/dt)
    v = math.sqrt(self.u*((2/r) - (1/self.a)))
    if (self.h/(r*v) > 1):
        print("Saved from a math error")
        phi = 0
    else:
        phi = math.acos(self.h/(r*v))
    self.Velocity = self.format64([v*math.cos(phi) + self.Parent.Velocity[0], v*math.sin(phi) + self.Parent.Velocity[1]])

    #print(); print(str(self.Name) + " jumped " + str(dTheta*ToDeg) + " degrees")
    #print(self.theta*ToDeg)

    # remove first pos, keeps from creating a huge array
    del self.PastPositions[:1]

    self.addPos2Past()


def ClassicalPhysicsEngine(bodyA, TIME_SCALAR):
### BODY PHYSICS ENGINE ###

	# ONLY CALCULATE IF OTHER BODY IS ONE OF THE FOLLOWING...
	#   - PARENT
	#   - STAR
	# 	- CHILD (ONLY FOR SUN)
	for bodyB in ALL_BODIES:
		if bodyB != bodyA and (bodyB == bodyA.Parent or bodyB == ALL_BODIES.getRoots()[0] or (bodyA == ALL_BODIES.getRoots()[0] and bodyB in bodyA.Children)):
			#print(); print(bodyA.Name)
			#print(">" + str(bodyB.Name))
			DistanceArray = bodyB.Position - bodyA.Position
			Distance = np.linalg.norm(bodyB.Position - bodyA.Position)
			angle = math.atan(DistanceArray[1]/DistanceArray[0])
			GForce = G*bodyB.Mass/(Distance*Distance)
			if bodyA.Position[0] > bodyB.Position[0]:
				ForceX = -math.cos(angle)*GForce[0]
				ForceY = -math.sin(angle)*GForce[0]
			else:
				ForceX = math.cos(angle)*GForce[0]
				ForceY = math.sin(angle)*GForce[0]
			bodyA.Velocity += TIME_SCALAR*np.array([ForceX,ForceY])


def PlayerPhysicsEngine(TIME_SCALAR):
	### PLAYER PHYSICS ENGINE ###

		for bodyA in PLAYER_OBJECTS:
			# 	ONLY DO NBODY CALCS ON PARENT(S) OF PARENT
			playerNBODs = []
			obj = bodyA
			#print("Nbod Calcs for Player " + str(player.indx) + " include...")
			while obj != None:
				if (obj.Name != "Player"):
					playerNBODs.append(obj)
				obj = obj.Parent
			for bodyB in playerNBODs:
				DistanceArray = bodyB.Position - bodyA.Position
				Distance = np.linalg.norm(bodyB.Position - bodyA.Position)
				angle = math.atan(DistanceArray[1]/DistanceArray[0])
				GForce = G*(bodyB.Mass)/(Distance*Distance)
				if bodyA.Position[0] > bodyB.Position[0]:
					ForceX = -math.cos(angle)*GForce[0]
					ForceY = -math.sin(angle)*GForce[0]
				else:
					ForceX = math.cos(angle)*GForce[0]
					ForceY = math.sin(angle)*GForce[0]
				ForceX += math.sin(bodyA.Angle*TORAD)*bodyA.Thrust
				ForceY -= math.cos(bodyA.Angle*TORAD)*bodyA.Thrust
				bodyA.Velocity += TIME_SCALAR*np.array([ForceX,ForceY])


# ==================================================
# RENDERER
# Handles:
#   - Iterating through all Stars, Planets, Moons and Calling Display Function
#   - Zoom
#   - Conversion of km to pixels
def Renderer(KM2PIX, Focus, SOI):

	for body in ALL_BODIES:
		#if (ENABLE_ELLIPSE_DRIVE and body.e_ != None):
		#	drawOrbit(body, KM2PIX, Focus)
		display(body, KM2PIX, Focus, SOI)

	#for obj in ALL_OBJECTS:
	#	display_Ojects(obj, KM2PIX, Focus)

	for player in PLAYER_OBJECTS:
		display_Player(player, KM2PIX, Focus)


def drawOrbit(self, KM2PIX, Focus):
	MiddlePoint = KM2PIX*(Focus - self.Parent.Position) 	# MiddlePoint = KM2PIX*(Focus - self.getBarycenter())
	Diameter = max(abs(self.a), abs(self.b))
	#print(self.Name)
	#print(MiddlePoint)
	try:
		int(MiddlePoint[0])
	except:
		print("critical error")
		print(str(self.Name) + " caused the critical error with an invalid MiddlePoint value of " + str(MiddlePoint))
		print("Position: " + str(self.Position))
		print("Velocity: " + str(self.Velocity))
		print("PastPos: " + str(len(self.PastPositions)))
		print("Focus: " + str(Focus))
		print("Parent: " + str(self.Parent))
		print("Parent Pos: " + str(self.Parent.Position))
		print("Parent Vel: " + str(self.Parent.Velocity))
		terminate()
		

	# Only show orbit if the body is in the frame
	CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
	CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

	if CheckXAxis and CheckYAxis:
		w = int(abs(2*self.a) * KM2PIX)
		h = int(abs(2*self.b) * KM2PIX)
		foci = self.Parent.Position 	# self.BaryCenter

		if (self.CircularOrbit):
			centerOfOrbit = KM2PIX * (foci - Focus)
		else:
			direcOfOrbit = self.e/self.e_
			centerOfOrbit = vecAdd(foci, (self.rmin - self.a)*direcOfOrbit)
			centerOfOrbit = KM2PIX * (centerOfOrbit - Focus)

		maxX = w+2
		displayX = DISPLAYSURF.get_size()[0]

		if (maxX < 2*displayX):
			drawEllipse(self,w,h,centerOfOrbit)
		#else:
		#	drawArc(self,w,h,centerOfOrbit)
			

def drawArc(self,w,h,centerOfOrbit):
	print("Draw an Arc Now...")

def drawEllipse(self,w,h,centerOfOrbit):
		Rect = pygame.Rect((1,1), (w+1,h+1))
		Surf = pygame.Surface((w+2,h+2))
		#Surf.fill(GRAY)
		Surf.set_alpha(100)
		if (w > 1):
			pygame.draw.ellipse(Surf, clrs['WHITE'], Rect, 1)
			#pygame.draw.rect(Surf, clrs['WHITE'], Rect, 1)
			Surf = pygame.transform.rotate(Surf, self.angle)
			(sx, sy) = Surf.get_size()
			#print([sx, sy])
			topLeft = np.array([int(centerOfOrbit[0] - sx/2), int(centerOfOrbit[1] + sy/2)], dtype = np.float64)
			DISPLAYSURF.blit(Surf, objectPos2ScreenXY(topLeft))

def objectPos2ScreenXY(pos):
	return [int(pos[0] + SURF_WIDTH/2), int(SURF_HEIGHT/2 - pos[1])]

# DISPLAY (for non-character/player bodies only)
def display(self, KM2PIX, Focus, SOI):
	MiddlePoint = KM2PIX*(self.Position - Focus)
	#print(self.Name)
	#print(MiddlePoint)
	if (MiddlePoint[0] == None):
		print("critical error")
		terminate()
	CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
	CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

	# ENABLING DISSAPPEARING BODIES
	# pixelSize = KM2PIX*self.Diameter/2
	# if CheckXAxis and CheckYAxis and pixelSize > 0.5
	if CheckXAxis and CheckYAxis:
		pygame.draw.circle(DISPLAYSURF, self.Color, (int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])), int(KM2PIX*(self.Diameter.round()/2)), 0)
		
		if SOI and self.SOI != None and self.SOI*KM2PIX > 1 and self.SOI*KM2PIX < SURF_WIDTH:
			pygame.draw.circle(DISPLAYSURF, FONT_COLOR, objectPos2ScreenXY(MiddlePoint), int(self.SOI*KM2PIX), 1)


def display_Player(self, KM2PIX, Focus):
	MiddlePoint = KM2PIX*(self.Position - Focus)
	CheckXAxis = -(SURF_WIDTH + self.Diameter*KM2PIX)/2 < MiddlePoint[0] < (SURF_WIDTH + self.Diameter*KM2PIX)/2
	CheckYAxis = -(SURF_HEIGHT + self.Diameter*KM2PIX)/2 < MiddlePoint[1] < (SURF_HEIGHT + self.Diameter*KM2PIX)/2

	if CheckXAxis and CheckYAxis:
		draw_angle = self.Angle + 180
		img = pygame.transform.rotate(self.Image, draw_angle)
		DISPLAYSURF.blit(img, objectPos2ScreenXY(MiddlePoint))


def objectPos2ScreenXY(MiddlePoint):
	return [int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])]



 
# ==================================================
# INTIALIZATION METHOD
# Handles:
#   - Creating and Defining Stars, Planets, Moons
#   - Creating Callable lists of Stars, Planets, Moons
def initialize_bodies():
	print()
	print("List of Bodies Created...")

	filename = 'solar.json'
	path = resource_path(os.path.join('resources',filename))
	all_bodies = System(path)
	return all_bodies

def initPlayer():
	print()
	print("Players created...")

	global PLAYER_OBJECTS
	path = resource_path(os.path.join('resources', 'player.json'))
	PLAYER_OBJECTS = System(path)
	player1 = PLAYER_OBJECTS.getRoots()[0]
	path = resource_path(os.path.join('resources', 'ghopper.jpg'))
	ghopper_img = load_image(path)
	player1.attachImage(ghopper_img)
	player1.addPlayerAttribs()
	Body = randomBody()
	player1.attachToBody(Body)

def randomBody():
	indx = int(len(ALL_BODIES.getRoots()[0].Children) * random.random())
	print(indx)
	return ALL_BODIES.getRoots()[0].Children[indx]

def load_image(path):
	"loads an image, prepares it for play"
	try:
		surface = pygame.image.load(path)
	except pygame.error:
		raise SystemExit('Could not load image "%s" %s'%(path, pygame.get_error()))
	return surface.convert()



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
	if FocusBody.getChildren():# and FocusBody.Name != siblings[0].Name:
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


# WRAPPING
def resource_path(relative):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative)
	return os.path.join(relative)

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

# VECTOR MATH
def vecAdd(vec1, vec2):
    return np.array([vec1[0] + vec2[0], vec1[1] + vec2[1]])
def vecSub(vec1, vec2):
    return np.array([vec1[0] - vec2[0], vec1[1] - vec2[1]])

# GET ANGLE FROM BODY TO PARENT
def getTheta(pos, par_pos):
    DistanceArray = vecSub(pos, par_pos)
    #print(DistanceArray)
    angle = math.atan(DistanceArray[1]/DistanceArray[0])
    if (pos[0] > par_pos[0]):
        return -angle
    else:
        return angle
# Print Theta
def printTheta(self):
	theta = getTheta(self.Position, self.Parent.Position)
	print(str(self.Name) + " is at angle " + str(getTheta(self.Position, self.Parent.Position)*TODEG))


# TERMINATE/CLOSE
def terminate():
	pygame.quit()
	sys.exit()


# CALLING THE PROGRAM
if __name__ == '__main__':
	main()