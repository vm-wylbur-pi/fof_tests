from typing import List, Dict, Union

import json
import os
import wave


AUDIO_INFO_FILE = 'audio/wav_meta.json'
WAV_FILE_DIR = '/Users/jeff/fof/audio_files/prepped_for_flowers'
NAME_KEY = "name"
DURATION_KEY = "duration_seconds"


def generate_wav_meta() -> List[Dict[str, Union[str, float]]]:
    wav_meta = []
    for root, _, files in os.walk(WAV_FILE_DIR):
        for filename in files:
            if filename.lower().endswith("wav"):
                path = os.path.join(root, filename)
                relative_path = path[len(WAV_FILE_DIR)+1:]
                print(f"Reading metadata for {relative_path}...")
                with wave.open(path) as audio:
                    duration_secs = audio.getnframes() / audio.getframerate()
                    params = audio.getparams()

                    wav_meta.append(
                        {
                            NAME_KEY: relative_path,
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
