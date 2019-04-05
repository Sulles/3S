"""
Created: April 2, 2019
Updated:

@author: Suleyman Barthe-Sukhera

This is a proof of concept stand-alone that uses pygame to demonstrate how EMEM can be created by objects and
received by sensors
"""


import sys
sys.path.append("..")
# from MessageTesting.Message import Message
import pygame
from Orbz.OrbManager import *
# import os
from pygame.locals import *
from time import time


'''
CONSTANTS
'''


def main():
    global DISPLAY_SURF, FPS_CLOCK, EMEM_RINGS, START_TIME
    pygame.init()
    DISPLAY_SURF = pygame.display.set_mode((SURF_WIDTH, SURF_HEIGHT))
    FPS_CLOCK = pygame.time.Clock()
    START_TIME = time()
    pygame.display.set_caption('Orbz')

    ALL_ORBZ = init_orbz()
    EMEM_MANAGER = emem_manager(ALL_ORBZ, DISPLAY_SURF)

    print("Successful init, running simulation...")

    # MAIN LOOP
    while True:

        DISPLAY_SURF.fill(BGCOLOR)

        for event in pygame.event.get():
            # EXIT CONDITION
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_ESCAPE):
                    terminate()

        for orb in ALL_ORBZ:
            orb.draw(DISPLAY_SURF)

        EMEM_MANAGER.update_emems(DISPLAY_SURF)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def init_orbz():
    locations = [[0, 0], [60, 0], [120, 0],
                 [-50, 50], [-150, 150], [100, -100]]
    colors = [RED, ORANGE, YELLOW, WHITERED, PALEBLUE, PURPLE]
    diameters = [14, 10, 8, 10, 20, 15]
    assert len(locations) == len(colors) == len(diameters), \
        "ORB CREATION ERROR: location, colors, and diameter array lengths do not match!"
    orbs = []
    for _ in range(len(locations)):
        orbs.append(orb(locations[_], colors[_], diameters[_]))
    return orbs


def terminate():
    pygame.quit()
    sys.exit()


''' RUN MAIN FUNCTION '''
if (__name__ == "__main__"):
    main()

