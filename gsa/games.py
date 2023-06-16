from dataclasses import dataclass
import random
import time
import os

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
#    velocity units are cm per second
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


# A circle of color that expands outward from (or contracts inward toward) a specified point.
# You can use this in various ways:
#    startRadius=0, positive velocity around 200: classic expanding wave of color after a step
#    startRadius non zero, 
@dataclass
class CircularColorWave(StatelessGame):
    hue: int
    center: geometry.Point
    startRadius: float
    speed: float  # Positive is growing, Negative is Shrinking. units are cm/sec

    def run(self, flowers):
        for flower in flowers:
            distanceFromCenter = self.center.diff(flower.location).magnitude()
            distanceFromStart = distanceFromCenter - self.startRadius
            timeToReachFlower = distanceFromStart / self.speed;
            if timeToReachFlower >= 0:
                millisToReachFlower = int(round(1000 * timeToReachFlower))
                # TODO: consider exposing hue pulse parameters as part of CircularColorWave, or maybe
                #       just make each pulse shorter the faster the wave speed.
                flower.HuePulse(hue=self.hue, startTime=f"+{millisToReachFlower}", rampDuration=200,
                                peakDuration=400, brightness=200)


# A moving spot of light on a flower, which jumps from flower to flower.
# The game-level logic controls which flower the fairy is on, and for how long.
# The flower-level code controls which part of the flower the fairy lights up,
# the speed of drift within the flower, the number of LEDs lit at a time.
@dataclass
class Fairy(StatefulGame):
    giggle_filenames = [
        "FoF_LilyGiggle1.WAV",
        "FoF_LilyGiggle2.wav",
        "FoF_LilyGiggle3.wav",
        "FoF_MikaylaCantCatch.wav",
        "FoF_MikaylaGiggle1.wav",
        "FoF_MikaylaGiggle2.wav",
        "FoF_MikaylaGiggle3.wav",
        "FoF_MikaylaGiggle4.wav",
        "FoF_MikaylaGiggle5.wav",
        "FoF_MikaylaGiggle6.wav",
        "FoF_MikaylaGiggle7.wav",
        "FoF_MikaylaOverHere1.wav",
        "FoF_MikaylaOverHere2.wav",
        "FoF_MikaylaOverHere_DOUBLE.wav",
        "FoF_MikaylaThisWay1.wav",
        "FoF_MikaylaThisWay_DOUBLE.wav",
        "FoF_PamMMgiggles.wav",
        "FoF_TaliaCantCatch1.wav",
        "FoF_TaliaCmonThisWay.wav",
        "FoF_TaliaGiggle1.wav",
        "FoF_TaliaGiggle2.wav",
        "FoF_TaliaGiggle3.wav",
        "FoF_TaliaGiggle4.wav",
        "FoF_TaliaOverHere.wav",
        "FoF_TaliaOverHere2.wav",
    ]
    giggles = {
        'Lily': [f for f in giggle_filenames if 'Lily' in f],
        'Talia': [f for f in giggle_filenames if 'Talia' in f],
    }

    def __init__(self, fairyName=None):
        # Behavior variables.  Constant for any game instance.
        self.secsPerVisitMean: float = 3.0
        self.secsPerVisitStDev: float = 2.0
        self.secsPerVisitMinimum: float = 0.5
        # Possible extension: add a specified color to the fairy. For now, it's gold.

        # State variables
        self.current_flower: Flower = None
        self.next_visit_time: int = 0
        if fairyName and fairyName in Fairy.giggles:
            self.fairyName = fairyName
        else:
            self.fairyName = random.choice(list(Fairy.giggles.keys()))
        self.giggle_sequence = list(Fairy.giggles[self.fairyName])
        random.shuffle(self.giggle_sequence)
        self.next_giggle_idx = 0

    def nextGiggleFilename(self):
        giggle_filename = self.giggle_sequence[self.next_giggle_idx]
        self.next_giggle_idx += 1
        if self.next_giggle_idx >= len(self.giggle_sequence):
            self.next_giggle_idx = 0
            # Change up the order of giggles for the next time we use each of them.
            random.shuffle(self.giggle_sequence)
        return giggle_filename


    def runLoop(self, flowers):
        now = time.time()
        if now > self.next_visit_time:
            candidates = flowers if self.current_flower is None else self.current_flower.findNClosestFlowers(flowers, 2)
            next_flower = random.choice(candidates)
            visitDuration = random.normalvariate(self.secsPerVisitMean, self.secsPerVisitStDev)
            visitDuration = max(visitDuration, self.secsPerVisitMinimum)
            # Visit duration is expected on the flower in milliseconds
            visitDurationMillis = int(round(visitDuration * 1000))
            next_flower.FairyVisit(visitDurationMillis)
            next_flower.PlaySoundFile(self.nextGiggleFilename())
            self.next_visit_time = now + visitDuration
            self.current_flower = next_flower
        
    def isDone(self):
        # TODO: we could specify a duration. For now, the only way to end the game
        #       is to clear all games.
        return False
