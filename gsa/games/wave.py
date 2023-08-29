# An interactive game in which waves of color spread outward from
# each person in the field. The waves are circular and spread outwards.
#
# Every N seconds, waves spread out from each place on the field where
# a person is, up to 3 people. If no people are detected, one wave is
# placed randomly.
#
# When a wave reaches a flower, it plays a sound. For each person, the sounds
# alternate between two syllables. Each syllable has six recordings, and the
# recording to use is randomized per-flower.
#
# When two waves intersect, the colors mix in interesting ways.

import random
import time

from . import game
from .color_waves import CircularColorWave
from ..game_state import GameState
from ..person import RandomizedAssignments


class Wave(game.StatefulGame):

    WAVE_SPEED = 500   # inches per second
    # How long to wait in between waves, in seconds
    INTERWAVE_DELAY = 7
    # Don't launch more waves than this, no matter how many people
    # the tracker says there are.
    MAX_WAVES = 3
    # How long in advance to schedule waves. Longer = smoother, but
    # shorter is more likely to be where a person was just detected.
    SCHEDULING_DELAY = 1000  # milliseconds

    ASSIGNABLE_HUES = (
        0,  # red
        32,  # orange
        64,  # yellow
        96,  # green
        128,  # aqua
        160,  # blue
        192,  # purple
        224,  # pink
    )

    def __init__(self, specSyllables=["G","Am", "Em"]):
        # Read configuration file (audio_files.yaml) which specifies the names
        # of the audio files for each syllable and which pairs of them go together.
        self.syllableAudioFiles = game.getAudioFiles()['Wave']['Syllables']
        self.specSyllables = specSyllables
        # The index of the next syllable (within self.specSyllables).
        # Unused if specSyllables is None
        self.nextSyllableIdx = 0

        # Which person has which color. Colors are 0-255 hues.
        self.hueAssignments = RandomizedAssignments(Wave.ASSIGNABLE_HUES)

        # The time when the next set of waves will be initiated.
        self.nextWaveTime: float = 0

    def chooseSoundFiles(self) -> 'list[str]':
        syllable = "unchosen"
        if self.specSyllables:
            syllable = self.specSyllables[self.nextSyllableIdx]
            self.nextSyllableIdx = (self.nextSyllableIdx + 1) % len(self.specSyllables)
        else:
            syllable = random.choice(list(self.syllableAudioFiles.keys()))
        return self.syllableAudioFiles.get(syllable, [])

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.nextWaveTime:
            # Update color and sound assignments. In case we do have consistent people,
            # They will get consistent colors. But this isn't needed for the experience.
            people = gameState.people.people
            self.hueAssignments.updateAssignments(people.keys())

            num_waves = 0
            for name, person in people.items():
                num_waves += 1
                if num_waves > Wave.MAX_WAVES:
                    break

                wave = CircularColorWave(
                    hue=self.hueAssignments.getAssignment(name),
                    center=person.location,
                    startRadius=0,
                    speed=Wave.WAVE_SPEED,
                    startTime=gameState.controlTimer() + Wave.SCHEDULING_DELAY,
                    soundFiles=self.chooseSoundFiles())
                wave.run(gameState.flowers)

            if not people:
                single_wave = CircularColorWave(
                    hue=random.choice(Wave.ASSIGNABLE_HUES),
                    center=gameState.field.randomPoint(),
                    startRadius=0,
                    speed=Wave.WAVE_SPEED,
                    startTime=gameState.controlTimer() + Wave.SCHEDULING_DELAY,
                    soundFiles=self.chooseSoundFiles()
                )
                single_wave.run(gameState.flowers)

            self.nextWaveTime = now + Wave.INTERWAVE_DELAY
