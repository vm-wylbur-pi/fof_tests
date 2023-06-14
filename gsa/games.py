from dataclasses import dataclass
import random
import time

from flower import Flower
import geometry

class Game:
    pass

class StatelessGame(Game):
    def run(self, flowers):
        # Send commands to flowers in order to run this game/effect.
        # This method must not block nor take too long.
        raise NotImplementedError

class StatefulGame(Game):
    # This method is called repeatedly, every time through the main game loop
    def runLoop(self, flowers):
        raise NotImplementedError

    # This method is called once per game loop. When it returns true, the game
    # is stopped, and runLoop will never be called again.
    def isDone(self):
        raise NotImplementedError

# A straight line of color that propagates perpendicular to itself.
# This is cool in itself and a useful building block for other effects.
#    velocity units are per second
@dataclass
class StraightColorWave(StatelessGame):
    hue: int
    start_loc: geometry.Point
    velocity: geometry.Vector

    def run(self, flowers):
        speed = self.velocity.magnitude()

        # slope is perpendicular to propagation direction, so invert x vs y
        # Also, follow right-hand-rule (90 deg turn from dir of propagation to get dir of slope.)
        line_vec = geometry.Vector(self.velocity.dy, self.velocity.dx)
        line = geometry.Line(self.start_loc, line_vec)
        for flower in flowers:
            perpVectorToFlower = line.perpendicularVectorTo(flower.location)
            inFrontOfLine = not perpVectorToFlower.contraryTo(self.velocity)
            print(f"Vector to flower {flower.id} {flower.location}: {perpVectorToFlower} (inFrontOfLine={inFrontOfLine})")
            if inFrontOfLine:
                millisToReachFlower = int(round(1000 * perpVectorToFlower.magnitude() / speed))
                # ramp and peak time could be parameters of this Game, or computed based on speed
                rampDuration = 200
                peakDuration = 400
                brightness = 200
                flower.HuePulse(hue=self.hue, startTime=f"+{millisToReachFlower}", rampDuration=rampDuration,
                                peakDuration=peakDuration, brightness=brightness)


# A moving spot of light on a flower, which jumps from flower to flower.
# The game-level logic controls which flower the fairy is on, and for how long.
# The flower-level code controls which part of the flower the fairy lights up,
# the speed of drift within the flower, the number of LEDs lit at a time.
@dataclass
class Fairy(StatefulGame):
    # Behavior variables.  Constant for any game instance.
    secsPerVisitMean: float = 3
    secsPerVisitStDev: float = 2
    secsPerVisitMinimum: float = 0.5
    # Possible extension: add a specified color to the fairy. For now, it's white.

    # State variables
    current_flower: Flower = None
    next_visit_time: int = 0

    def runLoop(self, flowers):
        now = time.time()
        if now > self.next_visit_time:
            candidates = flowers if self.current_flower is None else self.current_flower.findNClosestFlowers(2)
            next_flower = random.choice(candidates)
            visitDuration = random.normalvariate(self.secsPerVisitMean, self.secsPerVisitStDev)
            visitDuration = max(visitDuration, self.secsPerVisitMinimum)
            next_flower.FairyVisit(visitDuration)
            self.next_visit_time = now + visitDuration
        
    def isDone(self):
        # TODO: we could specify a duration. For now, the only way to end the game
        #       is to clear all games.
        return False
