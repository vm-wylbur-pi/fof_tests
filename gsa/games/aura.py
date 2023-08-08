# An interactive game in which each person in the field is assigned a color
# and all the flowers near them light up with their color. Their color follows
# them as they move around the field. When two or more people get near one another,
# their colors mix in interesting ways.

import random

from . import game
from ..game_state import GameState
from ..color import distantFromSetofHues, HSVAColor
from ..person import RandomizedAssignments

class Aura(game.StatefulGame):

    # Within this distance, flowers fully show blob color
    BLOB_FULL_STRENGTH_RADIUS = 100
    # Between the full-strength radus and the ramp radius, flowers
    # only show the blob's color partially.
    # Beyond the ramp radius, flowers are not affectedy by the blob.
    BLOB_RAMP_RADIUS = 150

    # How strong the color effect of a blob is as a function of radius (distance
    # from the person at its center).  Ranges from [0-1].  Zero means no effect.
    @classmethod
    def blobFalloff(cls, distToPerson):
        if distToPerson < Aura.BLOB_FULL_STRENGTH_RADIUS:
            return 1.0
        elif distToPerson < Aura.BLOB_RAMP_RADIUS:
            rampFraction = ((distToPerson - Aura.BLOB_FULL_STRENGTH_RADIUS) /
                            (Aura.BLOB_RAMP_RADIUS - Aura.BLOB_FULL_STRENGTH_RADIUS))
            return rampFraction
        else:
            return 0.0

    TRANSPARENT = HSVAColor(0, 0, 0, 0)  # only alpha=0 matters here
    # A set of distinguishable colors
    hueMenu = {
        0: 'red',
        32: 'orange',
        64: 'yellow',
        96: 'green',
        128: 'aqua',
        160: 'blue',
        192: 'purple',
        224: 'pink',
    }

    def __init__(self):
        # Which person has which color. Colors are 0-255 hues.
        self.hueAssignments = RandomizedAssignments(list(Aura.hueMenu.keys()))

    def runLoop(self, gameState: GameState):
        people = gameState.people.people
        if not people:
            # Nobody is in the field, no updates to the flowers are needed
            return
        self.hueAssignments.updateAssignments(people.keys())

        for flower in gameState.flowers:
            blobs = []
            for name, person in people.items():
                distToPerson = flower.location.distanceTo(person.location)
                if distToPerson < Aura.BLOB_RAMP_RADIUS:
                    blobs.append(person)

            hue, sat = 0, 255
            if len(blobs) == 0:
                # This flower is not in any blob
                flower.SetBlossomColor(Aura.TRANSPARENT)
                continue
            elif len(blobs) == 1:
                # This flower is near a single person; use their color
                hue = self.hueAssignments.getAssignment(blobs[0].name)
            elif len(blobs) <= 3:
                # Fun color mixing. Choose a color distant from the inputs
                hues = [self.hueAssignments.getAssignment(blob.name) for blob in blobs]
                hue = distantFromSetofHues(hues)
            else:
                # Four or more people, use white for the overlap
                hue, sat = 0, 255

            alpha = int(round(255 * Aura.blobFalloff(distToPerson)))
            flower.SetBlossomColor(HSVAColor(hue, sat, 255, alpha))


    def isDone(self):
        return False
    
    def stop(self, gameState):
        pass
