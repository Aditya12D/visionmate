from pathlib import Path
import wave
import sounddevice as sd
from piper.config import SynthesisConfig
import soundfile as sf

from piper.voice import PiperVoice
from config import PIPER_MODEL, PIPER_CONFIG

class PiperTTS:

    def __init__(self):
        self.voice = PiperVoice.load(
            model_path=PIPER_MODEL,
            config_path=PIPER_CONFIG
        )

    def speak(self, text: str):
        """
        Convert text to speech and play it.
        """
        config=SynthesisConfig(length_scale=1.2)
        output_path = "output.wav"

        with wave.open(output_path, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file, syn_config=config)

        audio, sample_rate = sf.read(output_path)

        sd.play(audio, sample_rate)
        sd.wait()