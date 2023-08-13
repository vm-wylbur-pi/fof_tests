from dataclasses import dataclass
import random
import time
 
from . import game
from ..field import Field
from ..flower import Flower
from ..game_state import GameState
from .. import geometry


# A straight line of color that propagates perpendicular to itself.
# This is cool in itself and a useful building block for other effects.
#    velocity units are cm per second
@dataclass
class StraightColorWave(game.StatelessGame):
    hue: int
    start_loc: geometry.Point
    velocity: geometry.Vector
    startTime: int  # control-timer time when the wave should start

    @classmethod
    def randomInstance(cls, gameState: GameState):
        startPoint = gameState.field.randomPointNearEdge()
        # Head toward the middle of the field, so the wave doesn't just start
        # near the edge and head outward, which would not be noticeable as a wave.
        target = gameState.field.center()
        waveSpeed = random.randint(300, 700)
        waveVelocity = target.diff(startPoint).norm().scale(waveSpeed)
        return StraightColorWave(hue=random.randint(0, 255),
                                 start_loc=startPoint,
                                 velocity=waveVelocity
                                 startTime:)

    def run(self, flowers: 'list[Flower]'):
        print(f"Running wave: {self}")
        speed = self.velocity.magnitude()

        # slope is perpendicular to propagation direction, so invert x vs y
        # Also, follow right-hand-rule (90 deg turn from dir of propagation to get dir of slope.)
        line_vec = geometry.Vector(self.velocity.dy, self.velocity.dx)
        line = geometry.Line(self.start_loc, line_vec)
        for flower in flowers:
            perpVectorToFlower = line.perpendicularVectorTo(flower.location)
            inFrontOfLine = not perpVectorToFlower.contraryTo(self.velocity)
            #print(f"Vector to flower {flower.id} {flower.location}: {perpVectorToFlower} (inFrontOfLine={inFrontOfLine})")
            if inFrontOfLine:
                millisToReachFlower = int(
                    round(1000 * perpVectorToFlower.magnitude() / speed))
                # ramp and peak time could be parameters of this Game, or computed based on speed
                rampDuration = 100
                peakDuration = 200
                brightness = 200
                flower.HuePulse(hue=self.hue, startTime=f"+{millisToReachFlower}", rampDuration=rampDuration,
                                peakDuration=peakDuration, brightness=brightness)


# A circle of color that expands outward from (or contracts inward toward) a specified point.
# Flowers will play one (randomly chosen from a list) sound when the wave reaches them.
# You can use this in various ways:
#    startRadius=0, positive velocity around 500: classic expanding wave of color after a step
#    startRadius non zero: contracting circle that draws color in toward a point.
@dataclass
class CircularColorWave(game.StatelessGame):
    hue: int
    center: geometry.Point
    startRadius: float
    speed: float  # Positive is growing, Negative is Shrinking. units are cm/sec
    soundFiles: 'list[str]' = None # Sounds to be triggered in flowers reached by the wave.

    @classmethod
    def randomInstance(cls, gameState: GameState):
        center = gameState.field.randomPoint()
        # We want to grow or shrink, but neither too fast nor noo slow.
        speed = random.randint(400, 700) * random.choice((1, -1))
        startRadius = 0 if speed > 0 else 700
        return CircularColorWave(hue=random.randint(0, 255),
                                 center=center, startRadius=startRadius, speed=speed,
                                 soundFiles=None)

    def run(self, flowers: 'list[Flower]'):
        print(f"Running wave: {self}")
        for flower in flowers:
            distanceFromCenter = self.center.diff(flower.location).magnitude()
            distanceFromStart = distanceFromCenter - self.startRadius
            timeToReachFlower = distanceFromStart / self.speed
            if timeToReachFlower >= 0:
                millisToReachFlower = int(round(1000 * timeToReachFlower))
                # TODO: consider exposing hue pulse parameters as part of CircularColorWave, or maybe
                #       just make each pulse shorter the faster the wave speed.
                rampDuration = 100
                peakDuration = 200
                brightness = 200
                flower.HuePulse(hue=self.hue, startTime=f"+{millisToReachFlower}", rampDuration=rampDuration,
                                peakDuration=peakDuration, brightness=brightness)
                if self.soundFiles:
                    flower.PlaySoundFile(filename=random.choice(self.soundFiles),
                                        startTime=f"+{millisToReachFlower}")


# Showcase wave effects by running through them with randomized parameters.
@dataclass
class RandomIdle(game.StatefulGame):
    # The set of field-level effects available for use
    field_effects_menu = (
        StraightColorWave,
        CircularColorWave,
    )

    def __init__(self):
        # Constants controlling the frequency of field-level effects.
        self.effectGapSecsMean: float = 4.0
        self.effectGapSecsStDev: float = 3.0
        self.effectGapSecsMinimum: float = 2.0
        # State variables
        self.next_effect_time: int = 0

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.next_effect_time:
            effect = random.choice(RandomIdle.field_effects_menu).randomInstance(gameState)
            effect.run(gameState.flowers)
            delay = random.normalvariate(self.effectGapSecsMean, self.effectGapSecsStDev)
            delay = max(delay, self.effectGapSecsMinimum)
            self.next_effect_time = now + delay
