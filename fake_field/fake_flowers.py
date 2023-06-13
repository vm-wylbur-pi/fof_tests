from dataclasses import dataclass
import time

import pygame

@dataclass
class FakeFlower:
    x: int
    y: int
    # MAC-address id for the flower, e.g. "AB:03:5D"
    id: str
    reference_time = 0
    patterns = []

    def draw(self, screen):
        time = self.controlMillis()
        led_state = LEDState(blossom_hue=0, leaf_hue=100);
        for pattern in self.patterns:
            led_state = pattern.modifyHue(time, led_state)

        pygame.draw.circle(screen, hueToPyGameColor(led_state.leaf_hue),
                           pygame.Vector2(self.x+4, self.y+4), radius=20)
        pygame.draw.circle(screen, hueToPyGameColor(led_state.blossom_hue),
                           pygame.Vector2(self.x, self.y), radius=20)

        # clear out finished patterns
        self.patterns = [p for p in self.patterns if not p.isDone()]

    def setReferenceTime(self, new_reference_time):
        self.reference_time = new_reference_time

    def controlMillis(self):
        # System time is used as a stand-in for NTP-synced time
        millis_since_epoch = int(round(time.time() * 1000))
        # Reference time behaves just like in the real flowers.
        return millis_since_epoch - self.reference_time

    def parseStartTime(self, startTimeParameter: str) -> int:
        if startTimeParameter.startswith("+"):
            offset = int(startTimeParameter[1:])
            return self.controlMillis() + offset
        else:
            return int(startTimeParameter)
    
    def addPattern(self, pattern_name, str_params):
        if pattern_name == "HuePulse":
            self.patterns += HuePulse(str_params)
            print(f"Flower {self.id} added HuePulse({str_params})")

    def clearPatterns(self):
        self.patterns = []



def hueToPyGameColor(hue:int):
    hueOn360Scale = int(round((360 * hue/255)))
    color = pygame.Color(0, 0, 0, 0)
    color.hsva = (hueOn360Scale, 100, 100, 100)
    return color


# Simplified representation of the colors of a flower's LEDs at a single point
# in time.  Uses the 0-255 hue scale of FastLED
@dataclass
class LEDState:
    blossom_hue: int
    leaf_hue: int


def makeFakeField():
    # TODO: Read these coordinates from a deployment file.
    return [
        FakeFlower(450, 100, "a"),
        FakeFlower(550, 200, "b"),
        FakeFlower(650, 300, "c"),
        FakeFlower(550, 400, "d"),
        FakeFlower(600, 250, "e"),
    ]

# An LED pattern within a single flower.  Analagous to the led_patterns::Pattern class
# in the flower microcontroler code, but simplified.
class FlowerPattern:
   pass

class HuePulse(FlowerPattern):
    def __init__(self, str_params):
        params = str_params.split(',')
        self.hue = 160 if len(params) < 1 else int(params[0])
        self.startTime = self.parseStartTime("+0") if len(params) < 2 else self.parseStartTime(params[1])
        self.rampDuration = 300 if len(params) < 3 else int(params[2])
        self.peakDuration = 600 if len(params) < 4 else int(params[3])
        self.brightness = 200 if len(params < 5) else int(params[4])

    def isDone(self, time: int):
        return time > (self.startTime + 2*self.rampDuration + self.peakDuration + 100)

    def modifyHue(self, time: int, prevState: LEDState) -> LEDState:
        if time < self.startTime:
            return prevState
        # Full pattern has finished; don't do any unnecessary work.
        #  TODO: replace 60, which is hard-coded as the max delayDueToHeight
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
            alpha = self.brightness
        elif patternTime < self.rampDuration + self.peakDuration + self.rampDuration:
            # Ramp the blossom back down to black
            timeIntoRamp = patternTime - self.rampDuration - self.peakDuration
            alpha = 1 - timeIntoRamp / self.rampDuration

        return LEDState(
            blossom_hue=alpha * self.hue + (1-alpha) * prevState.blossom_hue,
            leaf_hue=alpha * self.hue + (1-alpha) * prevState.leaf_hue,
        )
