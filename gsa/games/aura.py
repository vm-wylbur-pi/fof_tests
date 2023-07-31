import random

from . import game
from ..game_state import GameState
from ..flower import Flower
from ..color import distantFromSetofHues, HSVAColor
from geometry import Point

class Aura(game.StatefulGame):

    BLOB_RADIUS = 150

    # A set of distinguishable colors
    hueMenu = frozenset([0, 32, 64, 96, 128, 160, 192, 224])
    TRANSPARENT = HSVAColor(0, 0, 0, 0)  # only alpha=0 matters here

    def __init__(self):
        # Which person has which color. Colors are 0-255 hues.
        self.color_assignments = {}

    def chooseNextColor(self):
        if not self.color_assignments:
            return random.choice(list(Aura.hueMenu))
        else:
            used_colors = set(self.color_assignments.items())
            remaining_colors = Aura.hueMenu - used_colors
            if remaining_colors:
                return random.choice(list(remaining_colors))
            else:
                # This would be a lot of simultaneous people in the field.
                return random.randint(0,255)
    
    def updateColorAssignments(self, activePersonNames):
        assignedNames = list(self.color_assignments.keys())
        for name in assignedNames:
            if name not in activePersonNames:
                del self.color_assignments[name]

        for name in activePersonNames:
            if name not in self.color_assignments:
                self.color_assignments[name] = self.chooseNextColor()

    # TODO: This should probably be a utility function, since other games will
    # also need it.  Factor it out when that happens.
    #
    # TODO: This renders one blob at a time, so the most recently rendered
    # blob will overwrite the others.
    def renderBlob(self, flowers: 'list[Flower]', hue: int, location: Point):
        pass

    def runLoop(self, gameState: GameState):
        people = gameState.people.people
        self.updateColorAssignments(people.keys())

        for flower in gameState.flowers:
            blobs = []
            for name, person in people.items():
                distToPerson = flower.location.distanceTo(person.location)
                if distToPerson < Aura.BLOB_RADIUS:
                    blobs.append(person)

            hue, sat = 0, 25
            if len(blobs) == 0:
                # This flower is not in any blob
                flower.SetUpdatableColor(Aura.TRANSPARENT)
                continue
            elif len(blobs) == 1:
                # This flower is near a single person; use their color
                hue = self.color_assignments[blobs[0].name]
            elif len(blobs) <= 3:
                # Fun color mixing. Choose a color distant from the inputs
                hues = [self.color_assignments[blob.name] for blob in blobs]
                print(f"Choosing intersection of: {hues}")
                hue = distantFromSetofHues(hues)
            else:
                # Four or more people, use white for the overlap
                hue, sat = 0, 255

            # TODO: Make the color.alpha value depend on distance from the blob center
            flower.SetUpdatableColor(HSVAColor(hue, sat, 100, 255))


    def isDone(self):
        return False
    
    def stop(self, gameState):
        pass
