from dataclasses import dataclass


@dataclass()
class SoundFile:
    name: str
    duration_seconds: float
    framerate: int
    comptype: str


@dataclass
class LoopSound:
    sound_file: SoundFile
    last_play_at: float  # time in seconds
    next_play_at: float  # time in seconds