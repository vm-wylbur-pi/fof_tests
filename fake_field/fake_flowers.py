from dataclasses import dataclass
import os.path
import time
import yaml

import sys  # TODO temp

import pygame

# Used for text rendering.
# Done once at module load time since this is slow
pygame.init()
font = pygame.font.SysFont(None, 15)

@dataclass
class HSVAColor:
    # All components are in the range [0-255]
    hue: int
    sat: int = 0
    val: int = 100
    alpha: int = 255

@dataclass
class FakeFlower:
    x: int
    y: int
    # MAC-address id for the flower, e.g. "AB:03:5D"
    id: str
    num: str   # str for matching mqtt topic without conversion
    reference_time = 0
    patterns = []
    text: str = ""

    def draw(self, screen):
        time = self.controlMillis()
        led_state = LEDState(blossom_color=pygame.Color("grey"),
                             leaf_color=pygame.Color("green"));
        for pattern in self.patterns:
            led_state = pattern.modifyLEDState(time, led_state)

        pygame.draw.circle(screen, led_state.leaf_color,
                           pygame.Vector2(self.x+3, self.y+3), radius=15)
        pygame.draw.circle(screen, led_state.blossom_color,
                           pygame.Vector2(self.x, self.y), radius=15)

        if self.text and self.textStartTime < time < self.textExpirationTime:
            textImg = font.render(self.text, True, pygame.Color("white"))
            screen.blit(textImg, (self.x, self.y+20))

        # clear out finished patterns
        self.patterns = [p for p in self.patterns if not p.isDone(time)]

    def setEventReference(self, new_reference_time):
        self.reference_time = new_reference_time

    # Render a short piece of text next to the flower briefly.
    # This is used to show the flower playing a sound file, rebooting, or
    # other behaviors that are hard to render as graphics.
    # duration is in milliseconds.
    # startTime is a string start-time spec, which is either
    #   - an integer giving a controlMillis start time
    #   - a string starting with "+" giving a number of millis relative to now.
    def showText(self, text, duration=900, startTime=None):
        self.text = text
        if startTime:
            self.textStartTime = parseStartTime(self.controlMillis(), startTime)
        else:
            self.textStartTime = self.controlMillis()  # show immediately
        self.textExpirationTime = self.textStartTime + duration

    def controlMillis(self):
        # System time is used as a stand-in for NTP-synced time
        millis_since_epoch = int(round(time.time() * 1000))
        # Reference time behaves just like in the real flowers.
        return millis_since_epoch - self.reference_time
    
    def addPattern(self, pattern_name, str_params):
        self.patterns.append(self.constructPattern(pattern_name, str_params))

    def updatePattern(self, pattern_name, str_params):
        newInstance = self.constructPattern(pattern_name, str_params)
        idx_of_existing_pattern = None
        for idx, pattern in enumerate(self.patterns):
            if pattern.__class__.__name__ == pattern_name:
                idx_of_existing_pattern = idx
        if idx_of_existing_pattern:
            self.patterns[idx_of_existing_pattern] = newInstance
        else:
            self.patterns.append(newInstance)

    def constructPattern(self, pattern_name, str_params):
        if pattern_name == "HuePulse":
            return HuePulse(self.controlMillis(), str_params)
        if pattern_name == "FairyVisit":
            print(f"Flower {self.id} added FairyVisit({str_params})")
            return FairyVisit(self.controlMillis(), str_params)
        if pattern_name == "BlossomColor":
            return BlossomColor(str_params)
        print(f"ERROR: LED Pattern {pattern_name} is not supported by the fake field.")


    def clearPatterns(self):
        self.patterns = []

def parseStartTime(controlTime: int, startTimeParameter: str) -> int:
    if startTimeParameter.startswith("+"):
        offset = int(startTimeParameter[1:])
        return controlTime + offset
    else:
        return int(startTimeParameter)


# Simplified representation of the colors of a flower's LEDs at a single point in time
@dataclass
class LEDState:
    blossom_color: pygame.Color
    leaf_color: pygame.Color


def hueToPyGameColor(hue: int):
    hueOn360Scale = int(round((360 * hue/255)))
    color = pygame.Color(0, 0, 0, 0)
    try:
        color.hsva = (hueOn360Scale, 100, 100, 100)
    except ValueError:
        print(
            f"Tried to set with 360-scale hue of {hueOn360Scale} based on hue={hue}")
        raise
    return color

def hsv255ToPyGameColor(hue: int, sat: int, val: int):
    hue360 = int(round(360 * hue/255))
    sat100 = int(round(100 * sat/255))
    val100 = int(round(100 * val/255))
    color = pygame.Color(0, 0, 0, 0)
    try:
        color.hsva = (hue360, sat100, val100, 100)
    except ValueError:
        print(f"Error making PyGame color based on hsv={hue},{sat},{val}")
        raise
    return color

def makeFakeField():
    return [
        FakeFlower(450, 100, "a"),
        FakeFlower(550, 200, "b"),
        FakeFlower(650, 300, "c"),
        FakeFlower(550, 400, "d"),
        FakeFlower(600, 250, "e"),
    ]

# yaml_file_path must be relative to fake_field/
def makeFakeFieldFromDeploymentYAML(yaml_file_name):
    field = []
    yaml_file_path = os.path.join(os.path.dirname(__file__), yaml_file_name)
    with open(yaml_file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        for flower_mac, flower in config['flowers'].items():
            field.append(FakeFlower(x=flower['x'], y=flower['y'], id=flower_mac, num=str(flower['id'])))
    return field

# An LED pattern within a single flower.  Analagous to the led_patterns::Pattern class
# in the flower microcontroler code, but simplified.
class FlowerPattern:
   pass

class BlossomColor(FlowerPattern):
    def __init__(self, str_params):
        h, s, v, a = map(int, str_params.split(','))
        self.color = HSVAColor(h, s, v, a)  # Just used for alpha during rendering
        self.pycolor = hsv255ToPyGameColor(self.color.hue, self.color.sat, self.color.val)  # used for other components

    def isDone(self, time: int):
        return False
    
    def modifyLEDState(self, time: int, prevState: LEDState) -> LEDState:
        alpha = self.color.alpha/255
        return LEDState(
            blossom_color=prevState.blossom_color.lerp(self.pycolor, alpha),
            leaf_color=prevState.leaf_color,
        )


class HuePulse(FlowerPattern):
    def __init__(self, control_time, str_params):
        params = str_params.split(',')
        if params == ['']:
            params = []
        self.hue = 160 if len(params) < 1 else int(params[0])
        self.startTime = parseStartTime(control_time, "+0") if len(params) < 2 else parseStartTime(control_time, params[1])
        self.rampDuration = 300 if len(params) < 3 else int(params[2])
        self.peakDuration = 600 if len(params) < 4 else int(params[3])
        self.brightness = 200 if len(params) < 5 else int(params[4])

        # Convert to pygame representation for interpolation support.
        self.color = hueToPyGameColor(self.hue)

    def isDone(self, time: int):
        return time > (self.startTime + 2*self.rampDuration + self.peakDuration + 100)

    def modifyLEDState(self, time: int, prevState: LEDState) -> LEDState:
        if time < self.startTime:
            return prevState
        # Full pattern has finished; don't do any unnecessary work.
        if time > self.startTime + 2*self.rampDuration + self.peakDuration:
            return prevState

        patternTime = time - self.startTime
        alpha = 0

        # Case 0: pulse hasn't reached this part of the flower yet.
        if patternTime < 0:
            alpha = 0
        # Case 1: ramping up. Same for leaves and blossom.
        elif patternTime < self.rampDuration:
            alpha = patternTime / self.rampDuration
        elif patternTime < self.rampDuration + self.peakDuration:
            alpha = 1  # During the peak
        elif patternTime < self.rampDuration + self.peakDuration + self.rampDuration:
            # Ramp the blossom back down to black
            timeIntoRamp = patternTime - self.rampDuration - self.peakDuration
            alpha = 1 - timeIntoRamp / self.rampDuration

        return LEDState(
            blossom_color=prevState.blossom_color.lerp(self.color, alpha),
            leaf_color=prevState.leaf_color.lerp(self.color, alpha),
        )

class FairyVisit(FlowerPattern):
    def __init__(self, control_time, str_params):
        # Params is expected to be a single integer giving the fairy visit duration in millis.
        visitDuration = int(str_params)
        self.visitEndTime = control_time + visitDuration

    def isDone(self, time: int):
        return time > self.visitEndTime

    def modifyLEDState(self, time: int, prevState: LEDState) -> LEDState:
        # In the real flower, "fairy" means lighting up a handful of LEDs at a
        # random spot on the flower, moving that spot around slowly, maybe pulsing
        # the spot's brightness, and playing a giggle noise on the speaker.
        #
        # In this simplified fake flower, "fairy" means the blossom and leaf
        # take turns flashing white for as long as the fairy is visiting.
        inFlash = (time // 50) % 2 == 0   # alternate every 50 ms
        onBlossom = (time // 200) % 2 == 0  # alternate every 510 ms
        newState = LEDState(prevState.blossom_color, prevState.leaf_color)
        if inFlash:
            if onBlossom:
                newState.blossom_color = pygame.Color("white")
            else:
                newState.leaf_color = pygame.Color("white")
        return newState
