# NOTE: This game does not work well, so it is not hooked up to any
#       GSA commands. We can try it again if/when we get high-quality
#       person tracking. A simplified version is in wave.py.
#
# An interactive game in which waves of color spread outward from
# each person in the field. The waves are circular and spread outwards.
# Each person is assigned a color and waves starting from them are
# in that color.  Waves stop originating from a person when they stop
# moving.
#
# When a wave reaches a flower, it plays a sound. For each person, the sounds
# alternate between two syllables. Each syllable has six recordings, and the
# recording to use is randomized per-flower.
#
# When the waves of two people intersect, the colors mix in interesting ways.


from collections import defaultdict
import time

from . import game
from .color_waves import CircularColorWave
from ..game_state import GameState
from ..person import RandomizedAssignments


class WaveInteractive(game.StatefulGame):

    WAVE_SPEED = 500
    # How long to wait in between waves from the same person. As long as a person
    # is moving, they will emit waves this often.  Unit is seconds.
    INTERWAVE_DELAY = 1.5

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

    def __init__(self):
        # Read configuration file (audio_files.yaml) which specifies the names
        # of the audio files for each syllable and which pairs of them go together.
        self.audioFiles = game.getAudioFiles()['Wave']

        # Which person has which color. Colors are 0-255 hues.
        self.hueAssignments = RandomizedAssignments(Wave.ASSIGNABLE_HUES)
        # Which person has which pair of syllables. Each pair is a list of two strings.
        self.soundAssignments = RandomizedAssignments(self.audioFiles['SyllablePairs'])

        # For each person, whether the next sound is the First of the
        # two-syllable pair of sounds assigned to them. This is used
        # to implement the first/second alternation for each person.
        self.nextSyllableIsFirstOfPair = defaultdict(bool)

        # The absolute time when each person last emited a wave. Zero if they
        # have not yet emitted their first wave.
        self.lastWaveTimes: dict[str, int] = defaultdict(int)

    def chooseSoundFiles(self, name) -> 'list[str]':
        syllables = self.soundAssignments.getAssignment(name)
        syllable = syllables[0] if self.nextSyllableIsFirstOfPair[name] else syllables[1]
        self.nextSyllableIsFirstOfPair[name] = not self.nextSyllableIsFirstOfPair
        if syllable not in self.audioFiles['Syllables']:
            print(f"ERROR: no sound files configured for syllable {syllable}")
        return self.audioFiles['Syllables'].get(syllable, [])

    def runLoop(self, gameState: GameState):
        people = gameState.people.people
        if not people:
            # Nobody is in the field, so there are no waves to initiate.
            return
        self.hueAssignments.updateAssignments(people.keys())
        self.soundAssignments.updateAssignments(people.keys())

        now = time.time()
        for name, person in people.items():
            time_since_last_wave = now - self.lastWaveTimes[name]
            if person.isMoving() and time_since_last_wave > Wave.INTERWAVE_DELAY:
                wave = CircularColorWave(hue=self.hueAssignments.getAssignment(name),
                                         center=person.location,
                                         startRadius=0,
                                         speed=Wave.WAVE_SPEED,
                                         startTime=gameState.controlTimer(),
                                         soundFiles=self.chooseSoundFiles(name))
                wave.run(gameState.flowers)
                self.lastWaveTimes[name] = now
