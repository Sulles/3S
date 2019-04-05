from Orbz.Orb import *
from Orbz.util import *
import pygame


class emem_manager (object):
    # TODO: add emem receivers
    def __init__(self, emem_transmitters, surface): #, emem_receivers):
        """
        Init method for EMEM Manager. Just instantiates EMEMs from list of transmitters
        :param emem_transmitters: list of bodies that transmit emems
        :param emem_receivers: list of bodies that receive emems
        :return: Nothing
        """
        self.transmitters = emem_transmitters
        self.emems = []

        # initial spawn of EMEMs
        self.update_emems(surface)

    def add_transmitter(self, emem_transmitter):
        self.transmitters.append(emem_transmitter)

    def update_emems(self, surface):
        """
        Currently, this method opts to create few EMEMs and display all of them, rather than create the number we want
            to get to, and only display a few of them
        :return: Nothing
        """
        # check for out-of-range, and update radius size
        for emem in self.emems:
            if emem.get_radius() > SURF_WIDTH:
                self.emems.remove(emem)
            emem.update()

        # change this variable to draw all emems, or only one per body
        # TODO: make a list of references to emems that should be drawn
        # Current methodology is dependent on maxing out self.emems and only follows the last emems created
        draw_all = False
        if draw_all:
            self.draw_emems(surface)
        else:
            self.draw_emems(surface, [emem for emem in self.emems[-len(self.transmitters):]])

        # make more if there are fewer active emems than MAX_EMEMS_SHOWN
        if len(self.emems) < MAX_EMEMS_SHOWN - len(self.transmitters):
            for t in self.transmitters:
                data = '{ "diameter": "' + str(t.Diameter) + '", ' + \
                       '"color": "' + str(t.Color) + '" }'
                self.emems.append(OrbEMEM('dummy_identifier', data, t.get_position(), RAD_GROWTH_RATE))

    def draw_emems(self, surface, list_of_emems=None):
        if list_of_emems is None:
            for m in self.emems:
                pygame.draw.circle(surface, WHITE, object_pos_to_screen(m.get_spawn_point()), m.get_radius(), 1)
        else:
            for m in list_of_emems:
                pygame.draw.circle(surface, WHITE, object_pos_to_screen(m.get_spawn_point()), m.get_radius(), 1)