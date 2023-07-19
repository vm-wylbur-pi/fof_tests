from typing import List, Dict, Union

import json
import os
import wave


AUDIO_INFO_FILE = 'audio/wav_meta.json'
WAV_FILE_DIR = 'audio_files'
NAME_KEY = "name"
DURATION_KEY = "duration_seconds"


def generate_wav_meta() -> List[Dict[str, Union[str, float]]]:
    wav_meta = []
    for wav_name in os.listdir(WAV_FILE_DIR):
        with wave.open(f"{WAV_FILE_DIR}/{wav_name}") as audio:
            duration_secs = audio.getnframes() / audio.getframerate()
            params = audio.getparams()

            wav_meta.append(
                {
                    NAME_KEY: wav_name,
                    DURATION_KEY: duration_secs,
                    **dict(params._asdict()),
                }
            )
    return wav_meta


if __name__ == "__main__":
    wav_meta = generate_wav_meta()
    json_object = json.dumps(wav_meta, indent=4)

    with open(AUDIO_INFO_FILE, "w") as f:
        f.write(json_object)
