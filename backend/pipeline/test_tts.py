from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

tts.tts_to_file(
    text="Hello, this is a test.",
    language="en",
    speaker_wav="backend/assets/default_speaker.wav",
    file_path="test.wav",
)

print("SUCCESS")