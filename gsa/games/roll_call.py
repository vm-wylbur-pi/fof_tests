from dataclasses import dataclass
import random
import time

from . import game
from ..game_state import GameState
from ..flower import Flower
from ..person import RandomizedAssignments

# The flowers light up and say "I'm here" one by one in order across the field.
#
# This could be set up either stateless (send all commands out at once), or
# stateful (buffer them gradually.) I'm going with buffered given the concerns
# we have about wifi crowding.
class RollCall(game.StatefulGame):
    def __init__(self, gapBetweenCallsMillis: int = 500):
        # Behavior variables.  Constant for any game instance.
        self.gapBetweenCalls: float = gapBetweenCallsMillis / 1000  # Seconds
        # State variables
        self.nextCallTime: float = 0  # seconds since epoch, as returned by time.time()
        self.flowersToCall: 'list[Flower]' = None

    def runLoop(self, gameState: GameState):
        if self.flowersToCall is None:
            # On first call, determine the order of flowers to call
            # Sort by (x,y) location. Reverse since we'll pop() them off the end.
            self.flowersToCall = sorted(gameState.flowers, reverse=True,
                                        key=lambda f: (f.location.x, f.location.y))
            audioFiles = game.getAudioFiles()['RollCall']
            self.flowerSounds = RandomizedAssignments(assignableItems=audioFiles)
            self.flowerSounds.updateAssignments(activePersonNames=[f.id for f in self.flowersToCall])

        now = time.time()
        if now > self.nextCallTime and self.flowersToCall:
            flower = self.flowersToCall.pop()
            flower.HuePulse(hue=64, startTime='+0',
                            rampDuration=100, peakDuration=200, brightness=200)
            flower.PlaySoundFile(self.flowerSounds.getAssignment(flower.id), startTime='+0')
            self.nextCallTime = now + self.gapBetweenCalls

    def isDone(self):
        return self.flowersToCall is not None and len(self.flowersToCall) == 0
