import numpy as np

class Body(object):
    # INITIALIZING BODY
    def __init__(self, name, parent, dia, mass, vel, rad, color):

        print(name)
        self.Name = name
        self.Diameter = dia
        self.Mass = np.array([mass], dtype = np.float64)
        self.Color = color
        self.Parent = parent
        self.Children = []
        self.Velocity = np.array(vel, dtype = np.float64)

        # IF PARENT EXISTS, ASSUME POSITION AND VELOCITY ARE RELATIVE TO PARENT
        if parent!= None:
            self.Parent.Children.append(self)
            self.Position = np.array([rad,0], dtype = np.float64) + self.Parent.Position

            # ADDING SPHERE OF INFLUENCE IF PARENT EXISTS
            dist = np.linalg.norm(self.Position - self.Parent.Position)
            SOI = dist*((self.Mass/self.Parent.Mass)**(2/5))
            self.SOI = SOI

        else:
            self.Position = np.array([rad,0], dtype = np.float64)
            self.SOI = None


    # ADDERS
    def addChild(self, Child):
        self.Children.append(Child)

    # REMOVERS
    def removeChild(self, Child):
        del self.Children[Child]


    # GETTERS
    def getChildren(self):
        return self.Children
    def getParent(self):
        return self.Parent
	
	
		
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
