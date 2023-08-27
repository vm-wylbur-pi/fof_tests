from dataclasses import dataclass
import random
import time
from typing import Callable, Dict
 
from . import game
from ..field import Field
from ..flower import Flower
from ..game_state import GameState
from .. import geometry
from ..color import HSVAColor

# If you tell a flower to light up and to play audio at the exact
# same time, latency in the audio system means the sound comes
# a little late. To compensate. we delay the instruction to light
# up by this much.
SOUND_TO_PULSE_OFFSET_MILLIS = 200


# Superclass for StraightPulseWave and CircularPulseWave
# Flowers will play one (randomly chosen from a list) sound when the wave reaches them.
@dataclass
class PulseWave(game.StatelessGame):
    startTime: int  # control-timer time when the wave should start
    pulseRampDuration = 100
    pulsePeakDuration = 200
    # Sounds to be triggered in flowers reached by the wave.
    soundFiles: 'list[str]' = None
    def callPulseOn(self, flower: Flower, controlTime: int):
        # To be overridden by final child classes, to specialize for
        # HuePulse vs SatValPulse
        raise NotImplementedError


# A straight line of pulse that propagates perpendicular to itself.
# This is cool in itself and a useful building block for other effects.
#    velocity units are inches per second
@dataclass
class StraightPulseWave(PulseWave):
    start_loc: geometry.Point = None
    velocity: geometry.Vector = None

    @classmethod
    def randomInstance(cls, gameState: GameState):
        startPoint = gameState.field.randomPointNearEdge()
        # Head toward the middle of the field, so the wave doesn't just start
        # near the edge and head outward, which would not be noticeable as a wave.
        target = gameState.field.center()
        waveSpeed = random.randint(300, 700)
        waveVelocity = target.diff(startPoint).norm().scale(waveSpeed)
        return StraightPulseWave(start_loc=startPoint,
                                 velocity=waveVelocity,
                                 startTime=gameState.controlTimer())

    def secsToReachFlower(self, flower:Flower) -> float:
        perpVectorToFlower = self.line.perpendicularVectorTo(flower.location)
        inFrontOfLine = not perpVectorToFlower.contraryTo(self.velocity)
        #print(f"Vector to flower {flower.id} {flower.location}: {perpVectorToFlower} (inFrontOfLine={inFrontOfLine})")
        if not inFrontOfLine:
            return float("Inf")
        else:
            return perpVectorToFlower.magnitude() / self.speed


    def run(self, flowers: 'list[Flower]'):
        print(f"Running wave: {self}")
        self.speed = self.velocity.magnitude()
        # slope is perpendicular to propagation direction, so invert x vs y
        # Also, follow right-hand-rule (90 deg turn from dir of propagation to get dir of slope.)
        line_vec = geometry.Vector(self.velocity.dy, self.velocity.dx)
        self.line = geometry.Line(self.start_loc, line_vec)
        arrivals = [(self.secsToReachFlower(f), f) for f in flowers]
        arrivals.sort(key=lambda a: a[0])
        for secsToReachFlower, flower in arrivals:
            if secsToReachFlower != float("Inf"):
                millisToReachFlower = int(round(1000 * secsToReachFlower))
                controlTimerPulseTime = self.startTime + millisToReachFlower
                self.callPulseOn(flower, controlTimerPulseTime +
                                 SOUND_TO_PULSE_OFFSET_MILLIS)
                if self.soundFiles:
                    flower.PlaySoundFile(filename=random.choice(self.soundFiles),
                                         startTime=controlTimerPulseTime)

@dataclass
class StraightColorWave(StraightPulseWave):
    hue: int = 150 # 0-255
    brightness: int = 200 # 0-255

    @classmethod
    def randomInstance(cls, gameState: GameState):
        base = StraightPulseWave.randomInstance(gameState)
        return StraightColorWave(hue=random.randint(0, 255),
                                 start_loc=base.start_loc,
                                 velocity=base.velocity,
                                 startTime=base.startTime)
    
    def callPulseOn(self, flower: Flower, controlTime: int):
        flower.HuePulse(hue=self.hue,
                        startTime=controlTime,
                        rampDuration=self.pulseRampDuration,
                        peakDuration=self.pulsePeakDuration,
                        brightness=self.brightness)


@dataclass
class StraightSatValWave(StraightPulseWave):
    satChange: float = 0.8
    valChange: float = 0.8

    @classmethod
    def randomInstance(cls, gameState: GameState):
        base = StraightPulseWave.randomInstance(gameState)
        # Random change between 0.5 (dimmer) and 1.5 (brighter)
        return StraightSatValWave(satChange=random.random() + 0.5,
                                  valChange=1.0,
                                  start_loc=base.start_loc,
                                  velocity=base.velocity,
                                  startTime=base.startTime)

    def callPulseOn(self, flower: Flower, controlTime: int):
        flower.SatValPulse(satChange=self.satChange,
                           valChange=self.valChange,
                           startTime=controlTime,
                           rampDuration=self.pulseRampDuration,
                           peakDuration=self.pulsePeakDuration)

# A circle of pulse that expands outward from (or contracts inward toward) a specified point.
# You can use this in various ways:
#    startRadius=0, positive velocity around 500: classic expanding wave of color after a step
#    startRadius non zero: contracting circle that draws color in toward a point.
@dataclass
class CircularPulseWave(PulseWave):
    center: geometry.Point = None
    startRadius: float = 0.0
    speed: float = 400 # Positive is growing, Negative is Shrinking. units are in/sec

    @classmethod
    def randomInstance(cls, gameState: GameState):
        center = gameState.field.randomPoint()
        # We want to grow or shrink, but neither too fast nor noo slow.
        speed = random.randint(400, 700) * random.choice((1, -1))
        startRadius = 0 if speed > 0 else 700
        return CircularPulseWave(center=center, startRadius=startRadius,
                                 speed=speed, startTime=gameState.controlTimer())

    def timeToReachFlower(self, flower: Flower) -> float:
        distanceFromCenter = self.center.diff(flower.location).magnitude()
        distanceFromStart = distanceFromCenter - self.startRadius
        timeUntilArrival = distanceFromStart / self.speed
        return timeUntilArrival

    def run(self, flowers: 'list[Flower]'):
        print(f"Running wave: {self}")
        arrivals = [(self.timeToReachFlower(f), f) for f in flowers]
        arrivals.sort(key=lambda a: a[0])
        for timeToReachFlower, flower in arrivals:
            if timeToReachFlower >= 0:
                millisToReachFlower = int(round(1000 * timeToReachFlower))
                controlTimerPulseTime = self.startTime + millisToReachFlower
                # Delegate to subclass to call either HuePulse or SatValPulse
                self.callPulseOn(flower, controlTimerPulseTime + SOUND_TO_PULSE_OFFSET_MILLIS)
                if self.soundFiles:
                    flower.PlaySoundFile(filename=random.choice(self.soundFiles),
                                         startTime=controlTimerPulseTime)


@dataclass
class CircularColorWave(CircularPulseWave):
    hue: int = 120
    brightness: int = 200

    @classmethod
    def randomInstance(cls, gameState: GameState):
        base = CircularPulseWave.randomInstance(gameState)
        return CircularColorWave(hue=random.randint(0, 255),
                                 center=base.center,
                                 startRadius=base.startRadius,
                                 speed=base.speed,
                                 startTime=base.startTime)

    def callPulseOn(self, flower: Flower, controlTime: int):
        flower.HuePulse(hue=self.hue,
                        startTime=controlTime,
                        rampDuration=self.pulseRampDuration,
                        peakDuration=self.pulsePeakDuration,
                        brightness=self.brightness)

@dataclass
class CircularStickyColorWave(CircularColorWave):

    @classmethod
    def randomInstance(cls, gameState: GameState):
        base = CircularColorWave.randomInstance(gameState)
        return CircularStickyColorWave(hue=random.randint(0, 255),
                                 center=base.center,
                                 startRadius=base.startRadius,
                                 speed=base.speed,
                                 startTime=base.startTime)

    def callPulseOn(self, flower: Flower, controlTime: int):
        CircularColorWave.callPulseOn(self, flower, controlTime)
        flower.SetBlossomColor(HSVAColor(self.hue, 255,self.brightness, 255),
                               controlTime+self.pulseRampDuration)
        

@dataclass
class CircularSatValWave(CircularPulseWave):
    satChange: float = 0.8
    valChange: float = 0.8

    @classmethod
    def randomInstance(cls, gameState: GameState):
        base = CircularPulseWave.randomInstance(gameState)
        # Random change between 0.5 (dimmer) and 1.5 (brighter)
        return CircularSatValWave(satChange=random.random() + 0.5,
                                  valChange=1.0,
                                  center=base.center,
                                  startRadius=base.startRadius,
                                  speed=base.speed,
                                  startTime=base.startTime)

    def callPulseOn(self, flower: Flower, controlTime: int):
        flower.SatValPulse(satChange=self.satChange,
                           valChange=self.valChange,
                           startTime=controlTime,
                           rampDuration=self.pulseRampDuration,
                           peakDuration=self.pulsePeakDuration)

# Showcase wave effects by running through them with randomized parameters.
@dataclass
class RandomWaves(game.StatefulGame):
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
            effect = random.choice(RandomWaves.field_effects_menu).randomInstance(gameState)
            # Start in the future, to give time for communication to full field.
            # This only works for StraightColorWave and CircularColorWave right now.
            effect.startTime = gameState.controlTimer() + 5000
            effect.run(gameState.flowers)
            delay = random.normalvariate(self.effectGapSecsMean, self.effectGapSecsStDev)
            delay = max(delay, self.effectGapSecsMinimum)
            self.next_effect_time = now + delay


# Slowly expanding circles of mold change the color of the field
class Mold(game.StatefulGame):
    SCHEDULING_DELAY = 2000

    def __init__(self, wavePeriod: int = 15, waveSpeed=100):
        # Behavior variables.  Constant for any game instance.
        self.wavePeriod: int = wavePeriod  # Seconds
        self.nextWaveTime: float = 0  # seconds since epoch, as returned by time.time()
        self.waveSpeed = waveSpeed

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.nextWaveTime:
            mold_wave = CircularStickyColorWave(
                hue=random.randint(0, 255),
                center=gameState.field.randomPoint(),
                startRadius=0,
                speed=self.waveSpeed,
                startTime=gameState.controlTimer() + Mold.SCHEDULING_DELAY,
            )
            mold_wave.run(gameState.flowers)
            self.nextWaveTime = now + self.wavePeriod
