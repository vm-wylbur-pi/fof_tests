from dataclasses import dataclass

import pygame

@dataclass
class FakeFlower:
    x: int
    y: int
    # MAC-address id for the flower, e.g. "AB:03:5D"
    id: str
    patterns = []

    def draw(self, screen):
        time = pygame.time.get_ticks()  # stand in for control timer
        hue = 0
        for pattern in self.patterns:
            hue = pattern.modifyHue(time, hue)

        # TODO: make the leaf and blossom colors a state variable. 
        pygame.draw.circle(screen, "green", pygame.Vector2(self.x+3, self.y+3), radius=20)
        pygame.draw.circle(screen, "red", pygame.Vector2(self.x, self.y), radius=20)

        # clear out finished patterns
        self.patterns = [p for p in self.patterns if not p.isDone()]



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
@dataclass
class FlowerPattern:
   pass

@dataclass
class HuePulse(FlowerPattern):
    startTime: int
    hue: int
    rampDuration: int
    peakDuration: int
    brightness: int

    def isDone(self, time):
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
