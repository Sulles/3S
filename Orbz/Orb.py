"""
Created: April 3, 2019
Edited:

@author: Suleyman Barthe-Sukhera

This object uses Message as a parent class to simulate an EMEM travelling through space
"""



import sys
sys.path.append("..")
from copy import deepcopy
from Orbz.util import *
from MessageTesting.Message import Message
import pygame


class OrbEMEM (Message):
    def __init__(self, identifier, data, spawn_point, radius_growth_rate, radius=1):
        """
        :param identifier: A string used to distinguish between different messages
        :param data: A JSON structure given as a string, used to encode data about the type of EM signal it represents
        :param spawn_point: The point of origination of this particular EMEM (list of length 2)
        :param radius_growth_rate: Rate of growth of radius (in px/update)
        :param radius: Starting radius length (in px)
        :return None
        """

        self.status = 1  # IN_TRANSIT
        self.radius = radius
        self.radius_growth_rate = radius_growth_rate

        assert isinstance(spawn_point, list), "OrbEMEM creation error: spawn_point not type: list"
        assert len(spawn_point) == 2, "OrbEMEM creation error: spawn_point list not length 2"

        # Instantiate super class
        super(OrbEMEM, self).__init__(identifier, data, self.status, spawn_point)

    def update(self):
        self.radius += self.radius_growth_rate

    def get_radius(self):
        return int(self.radius)

    def get_spawn_point(self):
        return super(OrbEMEM, self).get_spawn_point()

    def warble_radius(self, adder):
        self.radius += adder


class orb (object):
    def __init__(self, loc, color=BLUE, diameter=50):
        assert len(loc) == 2
        self.Position = loc
        self.Color = color
        self.Diameter = diameter

    def draw(self, surface):
        pygame.draw.circle(surface, self.Color, object_pos_to_screen(self.Position), int(self.Diameter / 2), 0)

    def get_position(self):
        return deepcopy(self.Position)