#!/usr/bin/env python
# =============================================================
#               IMPORTING NECESSARY MODULES
# =============================================================
import asyncio, json, logging, websockets
import math, sys, os, time   # time.sleep(second input)
import numpy as np
import random as rm
from system import *
from datetime import datetime
from pygame import time as py_time
logging.basicConfig()


# =============================================================
#               INITIALIZING GLOBAL VARIABLES
# =============================================================
global USERS, SUPS, TIME_SCALAR, RUN_MAIN_GAME_LOOP, MAIN_GAME_LOOP_TIMER, PING, PONG, PINGPONG, MAX_PING_TIME, UPSCLOCK
USERS = set()
SUPS = 20    # Server Updates Per Second
TIME_SCALAR = (1/SUPS) * 1000
RUN_MAIN_GAME_LOOP = False
MAIN_GAME_LOOP_TIMER = 0
PING = []; PONG = []; PINGPONG = []; MAX_PING_TIME = 1000


# =============================================================
#                    MESSAGE PREPARERS
# =============================================================
def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})
def prep_user_msg(message):
    return json.dumps({'type': 'message', 'txt': message})
def prep_body_info(name, dia, pos, vel, parent, soi, color):
    return json.dumps({'type': 'add_body',  'Name': name,
                                            'Diameter': dia,
                                            'Position': pos,
                                            'Velocity': vel,
                                            'Parent': parent,
                                            'SOI': soi,
                                            'Color': color})
def prep_player_info(indx, dia, pos, vel, parent):
    return json.dumps({'type': 'add_player','Index': indx,
                                            'Diameter': dia,
                                            'Position': pos,
                                            'Velocity': vel,
                                            'Parent': parent})
def prep_body_update(bodyindex, pos, vel, accel):
    return json.dumps({'type': 'body_update',   'Index': bodyindex,
                                                'Position': pos,
                                                'Velocity': vel,
                                                'Acceleration': accel})
def prep_player_update(indx, pos, vel, accel):
    return json.dumps({'type': 'player_update', 'Index': bodyindex,
                                                'Position': pos,
                                                'Velocity': vel,
                                                'Acceleration': accel})

# =============================================================
#                     MESSAGE SENDERS
# =============================================================
async def send_updated_body(bodyindex, pos, vel, accel):
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = prep_body_update(bodyindex, pos, vel, accel)
        await asyncio.wait([user.send(message) for user in USERS])
async def send_updated_player(indx, pos, vel, accel):
    if USERS:
        message = prep_player_update(indx, pos, vel, accel)
        await asyncio.wait([user.send(message) for user in USERS])
async def update_user_numbers():
    if USERS:
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])
async def send_all_users(message):
    if USERS:
        message = prep_user_msg(message)
        await asyncio.wait([user.send(message) for user in USERS])
async def send_body_info(name, dia, pos, vel, parent, soi, color):
    if USERS:
        message = prep_body_info(name, dia, pos, vel, parent, soi, color)
        await asyncio.wait([user.send(message) for user in USERS])
async def send_player_info(indx, dia, pos, vel, parent):
    if USERS:
        message = prep_player_info(indx, dia, pos, vel, parent)
        await asyncio.wait([user.send(message) for user in USERS])
async def tell_clients(message):
    if USERS:
        message = json.dumps({'type': message})
        await asyncio.wait([user.send(message) for user in USERS])
async def send_user_message(user, message):
    if USERS:
        message = json.dumps({'type': 'message', 'txt': message})
        await asyncio.wait([user.send(message)])
async def send_user_ping(user):
    if USERS:
        message = json.dumps({'type': 'ping'})
        await asyncio.wait([user.send(message)])
async def send_users_their_player_index():
    if USERS:
        x = 0
        for user in USERS:
            message = json.dumps({'type': 'set_player_index', 'indx': str(x)})
            print(message)
            await asyncio.wait([user.send(message)])
            x += 1
async def send_users_init_bodies():
    for body in ALL_BODIES:
        name = str(body.Name); dia = int(body.Diameter); pos = deNumpy(body.Position); vel = deNumpy(body.Velocity); parent = str(body.Parent); color = body.Color; 
        if (body.SOI == None): soi = None
        else: soi = int(body.SOI)
        await send_body_info(name, dia, pos, vel, parent, soi, color)
async def send_users_init_players():
    for player in ALL_PLAYERS:
        indx = int(player.indx); dia = int(player.Diameter); pos = deNumpy(player.Position); vel = deNumpy(player.Velocity); parent = str(player.Parent.Name)
        await send_player_info(indx, dia, pos, vel, parent)


# =============================================================
#               CLIENT/SYSTEM REGISTRATION
# =============================================================
async def register(websocket):
    USERS.add(websocket)
    await update_user_numbers()
async def unregister(websocket):
    USERS.remove(websocket)
    await update_user_numbers()


# =============================================================
#               MAIN WEBSOCKETS SERVICE
# =============================================================
async def main(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['action'] == 'space':
                await send_all_users('Houston, we have a message!')
            elif data['action'] == 'start_game' and len(USERS) > 1:
                await startGame()
            elif data['action'] == 'start_timer':
                await tell_clients('start_timer')
            elif data['action'] == 'stop_timer':
                await tell_clients('stop_timer')
            elif data['action'] == 'send_ping':
                await doPing()
            elif data['action'] == 'pong':
                await updatePong(websocket)
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregister(websocket)

# =============================================================
#                       MAIN GAME LOOP
# =============================================================
async def MainGameLoop():
    UPSCLOCK = py_time.Clock()
    while True:
        # Start server tic timer
        START_UPS_TIC = UPSCLOCK.get_time()

        # Send updated Bodies while calculating next values
        for body in ALL_BODIES:
            await send_updated_body(int(body.indx), deNumpy(body.Position), deNumpy(body.Velocity), deNumpy(body.Acceleration))

        # Call Physics Engine
        ClassicalPhysicsEngine(TIME_SCALAR)

        # Server Tic timer
        if (UPSCLOCK.get_time() == 0): END_UPS_TIC = 0
        else:   END_UPS_TIC = int(1000/UPSCLOCK.get_time())
        print("Server Update Took: " + str(END_UPS_TIC) + " ms")

        # If a player leaves a body's SOI, physics engine needs to be tweaked (by changing player.Parent)
        checkPlayerParentSOI()

        UPSCLOCK.tick(SUPS)

    #else:
        #print("Not Running Game...")

# This function checks if the player has entered the sphere of influence of another body
def checkPlayerParentSOI():
    for player in ALL_PLAYERS:
        if (player.SOI != None):
            # First, check siblings (children of parent)
            for sibling in player.Parent.Children:
                if (sibling != player):
                    dist = abs(np.linalg.norm(player.Position - sibling.Position))
                    if (dist < sibling.SOI):                # If player is within SOI...
                        changePlayerParent(player, sibling)
                        break;                              # Break if this happens, SOI and parent is found
            # Second, check parent's siblings
            if (child.Parent.Parent != None):       # Ensure 2 parent's up isn't null (happens when player is orbiting the sun)
                for parent_sibling in player.Parent.Parent.Children:
                    dist = abs(np.linalg.norm(player.Position - parent_sibling.Position))
                    if (dist < parent_sibling.SOI):
                        changePlayerParent(player, parent_sibling)
                        break;
            # Third, check parent's parent if player is no longer in it's parent's SOI
            elif (abs(np.linalg.norm(player.Position - player.Parent.Position)) > player.Parent.SOI and child.Parent.Parent != None):
                changePlayerParent(player, player.Parent.Parent)
                break;

# Properly removes player from parent's children list and changes self.Parent property as well as adds self to new parent's children list
def changePlayerParent(self, newParent):
    print("Player " + str(self.indx) + " changed parent from " + str(self.Parent.Name) + " to " + str(newParent.Name))
    self.Parent.removeChild(self)   #   - Remove player from parent's children list
    self.Parent = newParent         #   - Update player's real paren
    self.Parent.addChild(self)      #   - Add player to parent's children list



# =============================================================
#               PINGING AND TIMING USERS
# =============================================================
async def doPing():
    if (len(PINGPONG) == 0):
        print("Analyzing Pings...")
        await send_all_users("Analyzing Pings...")
        global START_PING_TIME
        START_PING_TIME = getMilliSecTime()
    for user in USERS:
        startTime = getMilliSecTime()
        PING.append([user, startTime])
        await send_user_ping(user)
# Update info of Ping time and link to User
async def updatePong(user):
    endTime = getMilliSecTime()
    PONG.append([user, endTime])
    if (len(PONG) == len(PING)):        # once all users have returned ping...
        for x in range(0, len(PING)):   # match user to websocket address and add ping to PINGPONG
            for z in range(0, len(PONG)):
                if (PING[x][0] == PONG[z][0]):      # find same websocket address
                    PINGPONG.append([PING[x][0], (PONG[z][1] - PING[x][1])])    # compare ping and pong time stamps
        # Reset ping and pong after each user is pinged once
        PING.clear(); PONG.clear();
        # Repeat PingPong till we have N data points
        N = 100
        if (len(PINGPONG)%len(USERS) == 0 and getMilliSecTime() - START_PING_TIME > MAX_PING_TIME):
            await analyzePingPong()
            print("Ping analysis cut short, total pings analyzed: " + str(len(PINGPONG)/len(USERS)))
            PINGPONG.clear()
        elif (len(PINGPONG) / len(USERS) == N):
            await analyzePingPong()
            print("Pings Successfully Analyzed")
            PINGPONG.clear()    # Clear PINGPONG for next run
        elif (len(PINGPONG) / len(USERS) < N):
            await doPing()
# Find average ping for each user and send info to user
async def analyzePingPong():
    UserPings = [];
    for user in USERS:
        UserPings.append([user])
    for x in range(0, len(PINGPONG)):
        z = 0;
        for user in USERS:
            if (PINGPONG[x][0] == user):
                UserPings[z].append(PINGPONG[x][1])
            else: z += 1
    for x in range(0,len(USERS)):
        avg = mean(UserPings[x][1:])
        await send_user_message(UserPings[x][0], "Your Average Ping is: " + str(avg))
        if (avg > 20):
            print("WARNING: User " + str(x) + " has a delayed ping")
def mean(array):
    return int(sum(array)/len(array))
def getMilliSecTime():
    return int(round(time.time()*1000))


# =============================================================
#                    GAME INITIALIZATION
# =============================================================
# Start Game handles:
#   - Creating system
#   - Sending system info to clients
#   - Check ping of users
#   - Allow call to MainGameLoop
async def startGame():
    #await doPing()
    #await asyncio.sleep(0.1)
    await send_all_users('Game is Beginning, Spawning the Solar System...')
    await initialize_bodies()
    await send_all_users('System Initialized, Creating Playser')
    await initialize_players()
    for x in range (3,0,-1):
        await send_all_users('Game Loaded! Game starting in... ' + str(x))
        await asyncio.sleep(1)
    await send_all_users('Game has begun!')
    await send_users_init_players()
    await send_users_their_player_index()
    await send_users_init_bodies()
    MAIN_GAME_LOOP_TIMER = getMilliSecTime()
    await MainGameLoop()
async def initialize_bodies():
    global ALL_BODIES, ALL_BODIES_length
    filename = 'solar.json'
    path = resource_path(os.path.join('resources',filename))
    ALL_BODIES = System(path)
    x = 0
    for body in ALL_BODIES:
        body.indx = x
        x += 1
    ALL_BODIES_length = x;
    print("System Initialized")
async def initialize_players():
    global ALL_PLAYERS
    ALL_PLAYERS = []
    filename = 'player.json'
    path = resource_path(os.path.join('resources',filename))
    for x in range(0,len(USERS)):
        newP = newPlayer(path,x)
        ALL_PLAYERS.append(newP)
    print("Players Initialized")
def newPlayer(path, x):
    CutOut = System(path)
    Player = CutOut.getRoots()[0]
    #print("Player " + str(x) + " initialized at position " + str(Player.Position))
    Player.addPlayerAttribs()
    Body = randomBody()
    Player.attachToBody(Body)
    Player.indx = x
    #print("Player " + str(Player.indx) + " is orbiting " + str(Player.Parent.Name + " at a distance of " + str(Player.Parent.Position - Player.Position)))
    return Player
def randomBody():
	# Check that you aren't starting at the same point as another player
	repeated = False; determined = False
	while not determined:
		indxx = int(len(ALL_BODIES.getRoots()[0].Children)*rm.random()) # only init player around a planet
		for x in range(0,len(ALL_PLAYERS)-1):
			if (ALL_BODIES.getRoots()[0].Children[indxx] == ALL_PLAYERS[x].Parent):
				repeated = True
		if repeated: 	# if starting place is repeated, reset repeated and continue while loop
			repeated = False
		else: 			# if not repeated, indxx is determined and stop the while loop
			determined = True

	return ALL_BODIES.getRoots()[0].Children[indxx]
	#print("ERROR: No Parent Body for Player Selected, Body Index: " + indxx)
def format64(array):
    return np.array([array[0], array[1]], dtype = np.float64)


# =============================================================
#                    BODY PHYSICS ENGINE
# =============================================================
def ClassicalPhysicsEngine(TIME_SCALAR):
    for bodyA in ALL_BODIES:
        # ONLY CALCULATE IF OTHER BODY IS ONE OF THE FOLLOWING...
        #   - PARENT
        #   - STAR
        #   - CHILD (ONLY FOR SUN) << REMOVED FOR SMOOTHER GAMEPLAY AND FEWER N-BODIES >> 
        for bodyB in ALL_BODIES:
            if bodyB != bodyA and (bodyB == bodyA.Parent or bodyB == ALL_BODIES.getRoots()[0]): # or (bodyA == ALL_BODIES.getRoots()[0] and bodyB in bodyA.Children)):
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
                ForceX *= TIME_SCALAR; ForceY *= TIME_SCALAR
                bodyA.Acceleration = format64([ForceX,ForceY])
                bodyA.Velocity += format64([ForceX,ForceY])


    for player in ALL_PLAYERS:
        # ONLY CALCULATE FOR PARENTS, AND PARENTS OF PARENTS... ETC...
        playerNBODs = []
        obj = player
        #print("Nbod Calcs for Player " + str(player.indx) + " include...")
        while obj != None:
            if (obj.Name != "Player"):
                playerNBODs.append(obj)
                #print("-" + str(obj.Name))
            obj = obj.Parent
        for body in playerNBODs:
            #print("Player " + str(player.indx) + " did Nbods with " + str(body.Name))
            DistanceArray = body.Position - player.Position
            Distance = np.linalg.norm(body.Position - player.Position)
            angle = math.atan(DistanceArray[1]/DistanceArray[0])
            GForce = G*body.Mass/(Distance*Distance)
            if player.Position[0] > body.Position[0]:
                ForceX = -math.cos(angle)*GForce[0]
                ForceY = -math.sin(angle)*GForce[0]
            else:
                ForceX = math.cos(angle)*GForce[0]
                ForceY = math.sin(angle)*GForce[0]
            ForceX += math.sin(player.Angle)*GForce[0]
            ForceY -= math.cos(player.Angle)*GForce[0]
            ForceX *= TIME_SCALAR; ForceY *= TIME_SCALAR
            player.Acceleration = format64([ForceX,ForceY])
            player.Velocity += format64([ForceX,ForceY])

    # Push updated positions
    for body in ALL_BODIES:
        body.Position += TIME_SCALAR*body.Velocity
    for player in ALL_PLAYERS:
        player.Position += TIME_SCALAR*player.Velocity


# WRAPPING
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

# MAKING JSON APPROPRIATE
def deNumpy(vec):
    return [vec[0], vec[1]]


# TERMINATE/CLOSE
def terminate():
    sys.exit()


# CALLING THE PROGRAM
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(
        #websockets.serve(main, host='192.168.8.102', port=6789))
        websockets.serve(main, host='localhost', port=6789))
    asyncio.get_event_loop().run_forever()