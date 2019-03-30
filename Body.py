import numpy as np
import math
from BackEndData import G
ToRad = math.pi/180
ToDeg = 180/math.pi

def vecAdd(vec1, vec2):
    return np.array([vec1[0] + vec2[0], vec1[1] + vec2[1]])
def vecSub(vec1, vec2):
    return np.array([vec1[0] - vec2[0], vec1[1] - vec2[1]])
def getTheta(pos, par_pos):
    DistanceArray = pos - par_pos
    angle = math.atan(DistanceArray[1]/DistanceArray[0])
    if (pos[0] > par_pos[0]):
        return -angle
    else:
        return angle



class Body(object):
    # INITIALIZING BODY
    def __init__(self, name, parent, dia, mass, vel, rad, color, e):

        #print(name)
        self.Name = name
        self.Diameter = dia
        self.Mass = np.array(mass, dtype = np.float64)
        self.Color = color
        self.Parent = parent
        self.Children = []
        self.Velocity = np.array(vel, dtype = np.float64)
        self.Acceleration = np.array([0,0], dtype = np.float64)
        self.FuturePositions = []
        self.PastPositions = []
        self.PastVel = self.Velocity
        self.CircularOrbit = None
        self.theta = 0
        self.e = e
        self.indx = None

        # IF PARENT EXISTS, ASSUME POSITION AND VELOCITY ARE RELATIVE TO PARENT
        if parent != None:
            self.Parent.Children.append(self)
            self.Position = np.array([rad,0], dtype = np.float64) + self.Parent.Position

            # ADDING SPHERE OF INFLUENCE IF PARENT EXISTS
            dist = np.linalg.norm(self.Position - self.Parent.Position)
            SOI = dist*((self.Mass/self.Parent.Mass)**(2/5))
            self.SOI = SOI
        else:
            self.Position = np.array([rad,0], dtype = np.float64)
            self.SOI = None

        # ORBITAL MECHANICS PREPARATION
        # For bodies with eccentricity
        if parent != None and (e != 0 and e != None):
            self.CircularOrbit = False
            Position = self.Position - self.Parent.Position
            Velocity = self.Velocity - self.Parent.Velocity
            self.L = np.cross(Position, self.Mass*Velocity)
            self.h = self.L/self.Mass
            self.u = G*(self.Mass + self.Parent.Mass)
            v = abs(np.linalg.norm(Velocity))
            r = abs(np.linalg.norm(Position))
            self.e = (v*v/self.u - 1/r)*Position - (np.dot(Position, Velocity)/self.u)*Velocity
            self.angle = math.atan(self.e[1]/self.e[0])/ToRad
            self.e_ = np.linalg.norm(self.e)
            self.a = -0.5*self.u[0]/((v*v/2) - self.u[0]/r)
            self.p = self.a*(1-self.e_*self.e_)
            self.rmax = self.p/(1-self.e_)
            self.rmin = self.p/(1+self.e_)
            self.b = math.sqrt(abs(self.p*self.a))
            self.A = math.pi*self.a*self.b
            #self.P = (self.A/self.dAdt)
            #print("Orbit time: " + str(np.round(self.P,2)) + " seconds")
            #self.n = 2*math.pi/self.P

        # ORBITAL MECHANICS PREPARATION
        # For bodies in circular orbits (e=0)
        elif parent != None and e == 0:
            Position = self.Position - self.Parent.Position
            Velocity = self.Velocity - self.Parent.Velocity
            v = abs(np.linalg.norm(Velocity))
            r = abs(np.linalg.norm(Position))
            self.L = np.cross(Position, self.Mass*Velocity)
            self.h = self.L/self.Mass
            self.u = G*(self.Mass + self.Parent.Mass)
            self.e_ = 0
            self.angle = 0
            self.CircularOrbit = True
            self.w = Velocity/Position
            self.A = math.pi*r*r
            self.a = r
            self.b = r
            self.rmax = self.rmin = r

        # NO ORBYMECHS READY
        if (self.CircularOrbit == None):
            self.e_ = None
            print("WARNING: " + str(self.Name) + " is not prepared for the Ellipse Drive")



    ## ORBITAL MECHANICS PREPPING FUNCTIONS
    def GForce(self):
        bodyA = self
        bodyB = bodyA.Parent
        DistanceArray = bodyB.Position - bodyA.Position
        Distance = np.linalg.norm(bodyB.Position - bodyA.Position)
        return G*(bodyB.Mass + bodyA.Mass)/(Distance*Distance)
    def calculateEllipse(self, AnalysisTime, stepSize):
        area = 0
        for x in range (0, len(self.PastPositions)-1):
            area += self.fromPointsCalcTriangle(self.Parent.PastPositions[x], self.PastPositions[x], self.getOffsetPastPosition(x+1))
        self.dAdt = area/AnalysisTime
        self.P = (self.A/self.dAdt)
        self.n = 2*math.pi/self.P
        self.theta = getTheta(self.Position, self.Parent.Position)
    def getOffsetPastPosition(self, x):
        offset = vecSub(self.Parent.PastPositions[x], self.Parent.PastPositions[x-1])
        return vecSub(self.PastPositions[x], offset)
    def fromPointsCalcTriangle(self, p1, p2, p3):
        return 0.5*np.cross((p2-p1), (p3-p1))
    def addPos2Past(self):
        self.PastPositions.append(self.format64([self.Position[0], self.Position[1]]))
    def updateFromEllipse(self, dt, current_theta):
        print(str(self.Name) + " jumping from " + str(current_theta*ToDeg)) # + " to...")
        old_r = np.linalg.norm(self.Position - self.Parent.Position)
        dTheta = self.a*self.b*self.n*dt/(old_r*old_r)
        self.theta = current_theta + dTheta
        if (self.theta > 2*math.pi):
            self.theta -= 2*math.pi
        if (self.CircularOrbit):
            r = self.a
        else:
            r = (self.a*(1-self.e_*self.e_))/(1+self.e_*math.cos(self.theta))
        self.updatePosFromRTheta(r)
        self.updateAcc(dt)
        self.updateVel(dt)

        #print(); print(str(self.Name) + " jumped " + str(dTheta*ToDeg) + " degrees")
        #print(self.theta*ToDeg)

        # remove first pos, keeps from creating a huge array
        del self.PastPositions[:1]



    ### PLAYER BASED FUNCTIONS
    # A FEW BASIC DEFAULTS
    def addPlayerAttribs(self):
        self.Angle = 180
        self.dAngle = 0     # change in Angle
        self.Thrust = 0
    # ATTACH TO A BODY (OR PLANET)
    def attachToBody(self, Parent):
        self.Parent = Parent
        Parent.Children.append(self)
        print(Parent.Children)
        print(str(self.Parent.Name) + " has added " + str(self.Name) + " as a child")
        r = self.Parent.Diameter
        self.Position = self.format64([r + self.Parent.Position[0], self.Position[1] + self.Parent.Position[1]])
        # ASSUMING CIRCULAR ORBIT
        rself = np.linalg.norm(self.Position)
        rparent = np.linalg.norm(Parent.Position)
        r = abs(rself - rparent)
        v = math.sqrt(G*(self.Parent.Mass**2)/(r*(self.Mass + self.Parent.Mass)))
        self.Velocity = [0 , v + Parent.Velocity[1]]
        print(self.Velocity[1])
        print(Parent.Velocity[1])
    # REMOVE CHILD, USUALLY A PLAYER WHO HAS TRANSITIONED INTO ANOTHER BODY'S SOI
    def removeChild(self, child):
        if (len(Children) == 0):
            print("This body does not have any children to be removed")
        else:
            for x in range(0, len(Children)):
                if (Children[x].Name == child.Name):
                    del self.Children[x];
    # ADDING A CHILD, USUALLY A PLAYER WHO HAS ENTERED THIS BODY'S SOI


    # EDITORS
    def recalcTheta(self):
        DistanceArray = vecSub(self.Position, self.Parent.Position)
        #print(DistanceArray)
        angle = math.atan(DistanceArray[1]/DistanceArray[0])
        if (self.Position[0] > self.Parent.Position[0]):
            self.theta = - angle
        else:
            self.theta = angle
    def updateAcc(self, dt):
        self.Acceleration = self.format64(vecSub(self.Velocity, self.PastVel)/dt)
    def updateVel(self, dt):
        r = np.linalg.norm(self.Position - self.Parent.Position)
        v = math.sqrt(self.u*((2/r) - (1/self.a)))
        if (self.h/(r*v) > 1):
            print("Saved from a math error")
            phi = 0
        else:
            phi = math.acos(self.h/(r*v))
        self.Velocity = self.format64([v*math.cos(phi) + self.Parent.Velocity[0], v*math.sin(phi) + self.Parent.Velocity[1]])
    def changeAcc(self, aX, aY):
        self.Acceleration = np.array([aX,aY])
    def updatePosFromRTheta(self, r):
        pos = np.array([r*math.cos(self.theta), r*math.sin(self.theta)], dtype = np.float64) + self.Parent.Position
        self.Position = self.format64(self.rotatePoint(self.Parent.Position, pos, self.angle)) #rotatePoint(self.getBarycenter(), pos, self.angle)
    def format64(self, pt):
        return np.array([pt[0], pt[1]], dtype = np.float64)
    def rotatePoint(self, origin, point, angle):
        # https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
        angle *= ToRad
        [ox, oy] = origin
        [px, py] = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return [qx, qy]



    # ADDERS
    def addChild(self, Child):
        self.Children.append(Child)
    def attachImage(self, Image):
        self.Image = Image
    def changeAngle(self, angle):
        self.Angle += angle
        if (self.Angle > 360): self.Angle -= 360
        elif (self.Angle < -360): self.Angle += 360
    def changeThrust(self, thrust):
        self.Thrust += thrust


    # REMOVERS
    def removeChild(self, Child):
        del self.Children[Child]


    # GETTERS
    def getChildren(self):
        return self.Children
    def getParent(self):
        return self.Parent
    def getBarycenter(self):
        r = (self.GForce()/self.Mass) / (1 + self.Mass/self.Parent.Mass)
        unitR = vecSub(self.Position, self.Parent.Position) / (np.linalg.norm( vecSub(self.Position, self.Parent.Position)))
        #return r*unitR
        return self.Parent.Position


    # PRINTERS
    def printOrbitalMechanics(self):
        print("====================================="); 
        print("Orbital Calcs for " + str(self.Name))    
        print("Eccentricity: " + str(np.round(self.e_,2)) + "    at an angle of: " + str(np.round(self.angle)))
        print("Semi-latus rectum: " + str(np.round(self.p)))
        print("Max r: " + str(np.round(self.rmax)) + "    min r: " + str(np.round(self.rmin)))
        print("Semi-major axis: " + str(np.round(2*self.a)) + "    semi-minor axis: " + str(np.round(2*self.b)))
    def printOrbitTime(self):
        print("Orbit time of " + str(self.Name) + " is " + str(abs(np.round(self.P/(60*60*24),2))) + " days")
	
	
		
	# SYSTEM UTILIZERS
    def _str(self, depth):
        rslt = depth*3*" "+self.Name
        for i in self.Children:
            rslt += "\n"+depth*3*" "+i._str(depth+1)
        return rslt
    def show(self):
        return self._str(0)
    def __str__(self):
        return self.Name
    def __repr__(self):
        return self.Name+str(list(self.Velocity))