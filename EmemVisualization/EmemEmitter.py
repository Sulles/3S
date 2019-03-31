"""
Created: March 30, 2019
Updated:

@author: Suleyman Barthe-Sukhera

Creates a psuedo EMEM Emitter object for the visualization and testing purposes
"""

from copy import copy

class EmEmitter(object):
    def __init__(self, emit_timer):
        self.__emit_timer = emit_timer


class EmEmitBody(EmEmitter):
    def __init__(self, location, velocity, acceleration, emit_timer):
        assert isinstance(location, list), "ERROR: Location is not a list"
        assert isinstance(velocity, list), "ERROR: Velocity is not a list"
        assert isinstance(acceleration, list), "ERROR: Acceleration is not a list"
        assert len(location) == 2, "ERROR: Location length not 2"
        assert len(velocity) == 2, "ERROR: Velocity length not 2"
        assert len(acceleration) == 2, "ERROR: Acceleration length not 2"
        assert isinstance(emit_timer, int), "ERROR: Emit Timer is not an int"

        self.__loc = location
        self.__vel = velocity
        self.__accel = acceleration
        super(EmEmitBody, self).__init__(emit_timer)

        print("EM Emitter Body Successfully Initialized")

    def get_loc(self):
        return copy(self.__loc)

    def get_vel(self):
        return copy(self.__vel)

    def get_accel(self):
        return copy(self.__accel)

    def update_loc(self, new_loc):
        assert isinstance(new_loc, list), "ERROR: New location is not a list"
        assert len(new_loc) == 2, "ERROR: New location length not 2"
        self.__loc = new_loc

    def update_vel(self, new_vel):
        assert isinstance(new_vel, list), "ERROR: New velocity is not a list"
        assert len(new_vel) == 2, "ERROR: New velocity length not 2"
        self.__vel = new_vel

    def update_accel(self, new_accl):
        assert isinstance(new_accl, list), "ERROR: New acceleration is not a list"
        assert len(new_accl) == 2, "ERROR: New acceleration length not 2"
        self.__accel = new_accl


if __name__ == '__main__':
    loc = [0,0]
    vel = [0,0]
    accel = [0,0]
    test_EmEmitBody = EmEmitBody(loc, vel, accel, 10)
