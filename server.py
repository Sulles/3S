#!/usr/bin/env python
import asyncio
# import json
import logging
# import math
import sys
# import os
import time   # time.sleep(millisecond input)
from system import *
from datetime import datetime
import websockets

logging.basicConfig()
USERS = set()
PULSES = []
PULSES_Client_Index = []
PING = []; PONG = []; PINGPONG = []; MAX_PING_TIME = 1000


# ==================================================
## MESSAGE PREPARERS
def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})


def prep_user_msg(message):
    return json.dumps({'type': 'message', 'txt': message})


def prep_body_info(name, dia, pos, vel, e, isCircular, a, b, A, dAdt, parent, color):
    return json.dumps({'type': 'body',  'Name': name,
                                        'Diameter': dia,
                                        'Position': pos,
                                        'Velocity': vel,
                                        'e': e,
                                        'isCircular': isCircular,
                                        'a': a,
                                        'b': b,
                                        'A': A,
                                        'dAdt': dAdt,
                                        'Parent': parent,
                                        'Color': color})

# ==================================================
# MESSAGE SENDERS


async def update_user_numbers():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def send_all_users(message):
    if USERS:
        message = prep_user_msg(message)
        await asyncio.wait([user.send(message) for user in USERS])


async def send_body_info(name, dia, pos, vel, e, isCircular, a, b, A, dAdt, parent, color):
    if USERS:
        message = prep_body_info(name, dia, pos, vel, e, isCircular, a, b, A, dAdt, parent, color)
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


async def send_user_pulse_delay(user, delay):
    if USERS:
        message = json.dumps({'type': 'pulse_delay', 'delay': delay})
        await asyncio.wait([user.send(message)])


# ==================================================
# CLIENT/SYSTEM REGISTRATION

async def register(websocket):
    USERS.add(websocket)
    await update_user_numbers()


async def unregister(websocket):
    USERS.remove(websocket)
    await update_user_numbers()


async def main(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        #await websocket.send(state_event())
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
            elif data['action'] == 'pulse':
                time = str(datetime.now().strftime('%H:%M:%S'))
                addPulse(time, websocket)
                if (len(PULSES) == len(USERS)):
                    await checkAndFixOffsets()
                    PULSES.clear()
                    PULSES_Client_Index.clear()
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregister(websocket)


# ==================================================
# Ping

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


async def updatePong (user):
    endTime = getMilliSecTime()
    PONG.append([user, endTime])
    if (len(PONG) == len(PING)):        # once all users have returned ping...
        for x in range(0, len(PING)):   # match user to websocket address and add ping to PINGPONG
            for z in range(0, len(PONG)):
                if (PING[x][0] == PONG[z][0]):      # find same websocket address
                    PINGPONG.append([PING[x][0], (PONG[z][1] - PING[x][1])])    # compare ping and pong time stamps
        #for x in range(len(PINGPONG) - len(PING),len(PINGPONG)):
        #    msg = 'Your ping is: ' + str(PINGPONG[x][1])
        #    await send_user_message(PINGPONG[x][0], msg)
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


async def analyzePingPong():
    UserPings = []
    for user in USERS:
        UserPings.append([user])
    for x in range(0, len(PINGPONG)):
        z = 0;
        for user in USERS:
            if (PINGPONG[x][0] == user):
                UserPings[z].append(PINGPONG[x][1])
            else: z += 1
    for x in range(0,len(USERS)):
        await send_user_message(UserPings[x][0], "Your Average Ping is: " + str(mean(UserPings[x][1:])))


def mean(array):
    return int(sum(array)/len(array))


def getMilliSecTime():
    return int(round(time.time()*1000))


# ==================================================
# Pulse Handler

async def checkAndFixOffsets():
    maxP = max(PULSES)
    for x in range(0,len(PULSES)):
        PULSES[x] -= maxP
    for x in range(0,len(PULSES)):
        if (PULSES[x] != 0):
            msg = "your pulse is off by " + str(abs(PULSES[x]))
            await send_user_message(PULSES_Client_Index[x], msg)
            await send_user_pulse_delay(PULSES_Client_Index[x], abs(PULSES[x]))
        else:
            await send_user_message(PULSES_Client_Index[x], '')
    print("Max pulse difference among users: " + str(min(PULSES)))


def addPulse(time, websocket):
    t = int(time[6:8])
    t += int(time[3:5])*60
    t += int(time[0:2])*60*60
    print(t)
    PULSES.append(t)
    PULSES_Client_Index.append(websocket)


# ==================================================
# Start Game handles:
#   - Creating system
#   - Sending system info to clients
#   - Checking consistency of all body properties between clients

async def startGame():
    await send_all_users('Game is Beginning, Spawning the Solar System...')
    initialize_bodies()
    await send_all_users('Bodies Ceated, Initializing the Ellipse Drive...')
    spoolEllipseDrive()
    await sendClientsBodies()
    await send_all_users('Ellipse Drive Ready!')
    #await startPulseLoop()


async def sendClientsBodies():
    for body in ALL_BODIES:
        name = body.Name; pos = deNumpy(body.Position); vel = deNumpy(body.Velocity); dia = int(body.Diameter); color = body.Color
        if body.e_ == None:
            e = None; isCircular = body.CircularOrbit; a = None; b = None; A = None;  dAdt = None; parent = None;
        elif body.e_ != 0:
            isCircular = body.CircularOrbit; e = deNumpy(body.e); a = np.linalg.norm(body.a); b = np.linalg.norm(body.b); A = body.A; dAdt = body.dAdt; parent = body.Parent.Name;
        elif body.e_ == 0:
            isCircular = body.CircularOrbit; e = 0; a = np.linalg.norm(body.a); b = np.linalg.norm(body.b); A = body.A; dAdt = body.dAdt; parent = body.Parent.Name;
        else:
            print(str(body.Name) + " has an exceptional, and unaccounted for e: " + str(body.e))
        await send_body_info(name, dia, pos, vel, e, isCircular, a, b, A, dAdt, parent, color)


def initialize_bodies():
    global ALL_BODIES
    filename = 'solar.json'
    path = resource_path(os.path.join('resources',filename))
    ALL_BODIES = System(path)
    print("System Initialized")


# ==================================================
# Spooling the Ellipse Drive :
#   - Run the physics engine a few times and enable position 2 past accumulation
#   - Calculate dA/dt, necessary for the Ellipse Drive

def spoolEllipseDrive():
    # Spool steps times, the larger the number, the better the end results should be...
    steps  = 100
    TotalAnalysisTime = 1000            # keep TotalAnalysisTime large to avoid 0 area triangles
    stepSize = int(TotalAnalysisTime/steps)
    for x in range(0, TotalAnalysisTime, stepSize):
        for body in ALL_BODIES:
            ClassicalPhysicsEngine(body, stepSize)
            body.addPos2Past()
    for body in ALL_BODIES:
        if (body.e_ != None):
            body.calculateEllipse(TotalAnalysisTime, stepSize)
        else:
            print("WARNING: " + str(body.Name) + " WILL NOT PARTICIPATE IN THE ELLIPSE DRIVE")
    print("Ellipse Drive Spooled")


def ClassicalPhysicsEngine(bodyA, TIME_SCALAR):
### BODY PHYSICS ENGINE ###

    # ONLY CALCULATE IF OTHER BODY IS ONE OF THE FOLLOWING...
    #   - PARENT
    #   - STAR
    #   - CHILD (ONLY FOR SUN)
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
    for body in ALL_BODIES:
        body.Position += TIME_SCALAR*body.Velocity


# WRAPPING
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


# MAKING JSON APPROPRIATE
def deNumpy(vec):
    #print(vec)
    return [vec[0], vec[1]]


address = '192.168.8.101'
try:
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(main, host=address, port=6789))
    print("(=) SERVER STARTED")
    asyncio.get_event_loop().run_forever()

except Exception as e:
    print("ERROR 001: Websockets could not establish a connection to " + address)

finally:
    print("(=) SERVER TERMINATED")
