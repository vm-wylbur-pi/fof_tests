import random
import time
from typing import List

from . import game
from ..game_state import GameState
from ..field import Field
from ..flower import Flower
from ..geometry import Point, Vector
from ..color import HSVAColor

# A blob of color bounces around the field, making the poing
# bounce sound when it ricochets off the edge of the field.
class BouncingBlob(game.StatefulGame):
    def __init__(self, speed: int = 200, radius: int = 150):
        # Behavior variables.  Constant for any game instance.
        self.speed: int = speed    # inches per second
        self.radius: int = radius  # inches
        # State variables
        self.hue = random.randint(0, 255)
        self.location: Point = None
        self.velocity: Vector = None
        self.lastUpdateTime = None
        self.flowersPulsedSinceBounce = set()

    def runLoop(self, gameState: GameState):
        now = time.time()
        if self.lastUpdateTime is None:
            self.location = gameState.field.randomPointNearEdge()
            direction = Vector(random.random(), random.random()).norm()
            self.velocity = direction.scale(self.speed)
            self.lastUpdateTime = now
        else:
            secsSinceLastUpdate = time.time() - self.lastUpdateTime
            displacement = self.velocity.scale(secsSinceLastUpdate)
            self.location = self.location.moveBy(displacement)
            self.bounceIfNeeded(gameState)
            self.renderBlob(gameState.flowers)

        self.lastUpdateTime = now
    
    def bounceIfNeeded(self, gameState: GameState):
        x, y, r, v = self.location.x, self.location.y, self.radius, self.velocity
        hitLeft   = v.dx < 0 and x-r < 0
        hitRight  = v.dx > 0 and x+r > gameState.field.width
        hitTop    = v.dy < 0 and y-r < 0
        hitBottom = v.dy > 0 and y+r > gameState.field.height
        if hitLeft or hitRight:
            self.velocity.dx *= -1
        if hitTop or hitBottom:
            self.velocity.dy *= -1
        if hitLeft or hitRight or hitTop or hitBottom:
            self.flowersPulsedSinceBounce.clear()
            flower = gameState.closestFlowerTo(self.location)
            flower.PlaySoundFile("mallets/Am_Balafon_Enote.wav")  # TODO: add delay matching the delay used for hue pulse
            print(f"Blob bounced at {self.location}, playing bounce sound on flower {flower.num}")
            print(f"New Velocity: {self.velocity}")

    def renderBlob(self, flowers: List[Flower]):
        for flower in flowers:
            distToBlobCenter = flower.location.distanceTo(self.location)
            if distToBlobCenter < self.radius and flower not in self.flowersPulsedSinceBounce:
                # The leading edge of the blob just hit a new flower. We need to calculate
                # how long it should light up, based on how far it is from the path of the
                # blob's center.
                vecToFlower = flower.location.diff(self.location)  # Should normalize to blob radius?
                chordLengthInBlob = 2 * vecToFlower.dot(self.velocity) / self.velocity.magnitude()
                timeInBlob = chordLengthInBlob / self.speed
                timeInBlobMillis = int(round(1000 * timeInBlob))
                flower.HuePulse(self.hue, startTime="+0", peakDuration=timeInBlobMillis)
                self.flowersPulsedSinceBounce.add(flower)
