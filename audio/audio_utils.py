import json
from dataclasses import fields
from typing import List, Dict, Any

from gsa.game_models import SoundFile
from scripts.generate_wav_info import AUDIO_INFO_FILE


def get_all_sounds() -> List[SoundFile]:
    with open(AUDIO_INFO_FILE, 'r') as file:
        sounds: List[Dict[str, Any]] = json.load(file)
    valid_keys = set(f.name for f in fields(SoundFile))
    return [
        SoundFile(
            **{k: v for k, v in sound.items() if k in valid_keys}) for sound in sounds
    ]
