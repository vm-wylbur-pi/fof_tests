from dataclasses import dataclass
import functools
import random
import textwrap
import time
import os
import yaml

from flower import Flower
from field import Field
import geometry

class Game:
    # Factory method to construct a randomized instance of a game.
    @classmethod
    def randomInstance(cls, field: Field):
        raise NotImplementedError

class StatelessGame(Game):
    def run(self, flowers):
        # Send commands to flowers in order to run this game/effect.
        # This method must not block nor take too long.
        raise NotImplementedError

class StatefulGame(Game):
    # This method is called repeatedly, every time through the main game loop
    def runLoop(self, flowers, field):
        raise NotImplementedError

    # This method is called once per game loop. When it returns true, the game
    # is stopped, and runLoop will never be called again.
    def isDone(self):
        raise NotImplementedError
    
    # This method is called to end the game. It gives the game a chance to
    # clean up any external state, such as retained MQTT messages, and/or
    # sending commands to flowers to end indefinitely-running patterns.
    def stop(self, flowers):
        raise NotImplementedError

# Reads the configuration file containing the set of audio files available to games.
@functools.lru_cache
def getAudioFiles():
    # Assumed to be in the same directory as main.py
    AUDIO_CONFIG_YAML_FILE = "audio_files.yaml"
    yaml_file_path = os.path.join(os.path.dirname(__file__), AUDIO_CONFIG_YAML_FILE)
    with open(yaml_file_path, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

# A straight line of color that propagates perpendicular to itself.
# This is cool in itself and a useful building block for other effects.
#    velocity units are cm per second
@dataclass
class StraightColorWave(StatelessGame):
    hue: int
    start_loc: geometry.Point
    velocity: geometry.Vector

    @classmethod
    def randomInstance(cls, field: Field):
        startPoint = field.randomPointNearEdge()
        # Head toward the middle of the field, so the wave doesn't just start
        # near the edge and head outward, which would not be noticeable as a wave.
        target = field.center()
        waveSpeed = random.randint(300,700)
        waveVelocity = target.diff(startPoint).norm().scale(waveSpeed);
        return StraightColorWave(hue=random.randint(0,255),
                                 start_loc=startPoint,
                                 velocity=waveVelocity)

    def run(self, flowers):
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

    @classmethod
    def randomInstance(cls, field: Field):
        center = field.randomPoint()
        # We want to grow or shrink, but neither too fast nor noo slow.
        speed = random.randint(400, 700) * random.choice((1, -1))
        startRadius = 0 if speed > 0 else 700
        return CircularColorWave(hue=random.randint(0,255),
                                 center=center, startRadius=startRadius, speed=speed)

    def run(self, flowers):
        print(f"Running wave: {self}")
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


class WholeFieldSleep(StatefulGame):
    def __init__(self, sleepIntervalSecs=5):
        self.hasSetRetainedSleepCommand = False
        self.sleepIntervalSecs = 5 * 60

    def runLoop(self, flowers, unused_field):
        if not self.hasSetRetainedSleepCommand:
            print("Setting retained sleep mode commands.")
            for flower in flowers:
                # This is a "Retained" MQTT message, which means the flowers will get it
                # right away, and will get it again every time they subscribe. Since they
                # re-subscribe to their MQTT command topic after waking from sleep, this
                # has the effect of keeping them asleep until the retained message is removed.
                flower.sendMQTTCommand(command="enterSleepMode",
                                       params=f'{self.sleepIntervalSecs * 1000}',
                                       retained=True)
            self.hasSetRetainedSleepCommand = True

    def isDone(self):
        # Keep the field asleep until this game is force-ended via the clearGames command
        return False
    
    def stop(self, flowers):
        print("Clearing retained sleep commands.")
        for flower in flowers:
            # You clear a retained MQTT message by sending a new one with an empty payload
            # If any flowers are currently awake (unlikely), this will cause them to sleep
            # one more time, for the default sleep duration (10 seconds)
            flower.sendMQTTCommand(command="enterSleepMode", params='', retained=True)


# A moving spot of light on a flower, which jumps from flower to flower.
# The game-level logic controls which flower the fairy is on, and for how long.
# The flower-level code controls which part of the flower the fairy lights up,
# the speed of drift within the flower, the number of LEDs lit at a time.
@dataclass
class Fairy(StatefulGame):
    def __init__(self):
        # Behavior variables.  Constant for any game instance.
        self.secsPerVisitMean: float = 3.0
        self.secsPerVisitStDev: float = 2.0
        self.secsPerVisitMinimum: float = 0.5
        # Possible extension: add a specified color to the fairy. For now, it's gold.

        # State variables
        self.current_flower: Flower = None
        self.next_visit_time: int = 0

        fairy_audio_files = getAudioFiles()['Fairy']
        self.fairyName = random.choice(list(fairy_audio_files.keys()))
        self.giggle_sequence = list(fairy_audio_files[self.fairyName])
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


    def runLoop(self, flowers, unused_field):
        now = time.time()
        if now > self.next_visit_time:
            candidates = flowers if self.current_flower is None else self.current_flower.findNClosestFlowers(flowers, 3)
            next_flower = random.choice(candidates)
            visitDuration = random.normalvariate(self.secsPerVisitMean, self.secsPerVisitStDev)
            visitDuration = max(visitDuration, self.secsPerVisitMinimum)
            # Visit duration is expected on the flower in milliseconds
            visitDurationMillis = int(round(visitDuration * 1000))
            next_flower.FairyVisit(visitDurationMillis)
            next_flower.PlaySoundFile(self.nextGiggleFilename())
            self.next_visit_time = now + visitDuration
            self.current_flower = next_flower
        
    def stop(self, unused_flowers):
        # The Fairy game only uses finite-duration patterns and audio clips, so
        # there is nothing that needs to be cleaned up when it stops.
        pass
    
    def isDone(self):
        # TODO: we could specify a duration. For now, the only way to end the game
        #       is to clear all games.
        return False

# Showcase field-level effects by running through several of them with randomized parameters.
@dataclass
class RandomIdle(StatefulGame):
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

    def runLoop(self, flowers, field):
        now = time.time()
        if now > self.next_effect_time:
            effect = random.choice(RandomIdle.field_effects_menu).randomInstance(field)
            effect.run(flowers)
            delay = random.normalvariate(self.effectGapSecsMean, self.effectGapSecsStDev)
            delay = max(delay, self.effectGapSecsMinimum)
            self.next_effect_time = now + delay

    def isDone(self):
        # Runs indefinitely, until explicitly stopped, usually through a
        # clearGames command sent to the GSA
        return False

    def stop(self, flowers):
        # We're only running short-duration effects, so there's nothing to do when stopping
        pass

@dataclass
class FunScreenText(StatefulGame):
    # How long between text changes on each individual flower.
    per_flower_change_interval_secs = 3 * 60

    def __init__(self):
        self.first_run = True
        self.nextFlowerIdx = 0
        self.nextChangeTime = 0
        self.readMessagesFromDataFile()
        self.msgGenerator = self.makeMessageGenerator()

    def readMessagesFromDataFile(self):
        # This is hard-coded for now, no real reason not to...
        msg_filename = "fun_screen_messages.txt"
        msg_path = os.path.join(os.path.dirname(__file__), msg_filename)
        self.messages = []
        with open(msg_path, 'r') as msg_lines:
            for line in msg_lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # If we change the font size on the screen, this width should change too.
                    wrapped_msg = '\n'.join(textwrap.wrap(line, width=9))
                    self.messages.append(wrapped_msg)
        print(f'FunScreenText read {len(self.messages)} from {msg_filename}')
    
    def makeMessageGenerator(self):
        while True:
            random.shuffle(self.messages)
            for message in self.messages:
                yield message

    def runLoop(self, flowers, unused_field):
        if not flowers:
            return
        if self.first_run:
            # Put a message on every flower, before starting to change them.
            for flower in flowers:
                flower.SetScreenText(next(self.msgGenerator))
            self.first_run = False
        else:
            now = time.time()
            if now > self.nextChangeTime:
                flowers[self.nextFlowerIdx].SetScreenText(next(self.msgGenerator))
                self.nextFlowerIdx = (self.nextFlowerIdx + 1) % len(flowers)
                delay = self.per_flower_change_interval_secs / len(flowers)
                self.nextChangeTime = now + delay

    def isDone(self):
        return False  # Runs indefinitely
    
    def stop(self, flowers):
        # TODO: Add a screen/showFlowerInfo command to each flower, and call
        # it here, to return each flower display to the debug info showing
        # the flower identifiers and firmware build details.
        pass  
