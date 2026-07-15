from pathlib import Path
import wave
import sounddevice as sd
from piper.config import SynthesisConfig
import soundfile as sf
import io

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
        Convert text to speech and play it locally on the laptop.
        """
        config = SynthesisConfig(length_scale=1.2)
        output_path = "output.wav"

        with wave.open(output_path, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file, syn_config=config)

        audio, sample_rate = sf.read(output_path)

        sd.play(audio, sample_rate)
        sd.wait()

    def save_to_file(self, text: str, output_path: str):
        """
        Synthesizes text to speech and saves it directly to the designated network path 
        without playing it out loud on the laptop speakers.
        """
        config = SynthesisConfig(length_scale=1.2)

        # Uses the identical, verified working method from your speak function
        with wave.open(output_path, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file, syn_config=config)

    def get_audio_bytes(self, text: str) -> bytes:
        """
        Synthesizes text to speech and returns the WAV bytes directly in memory.
        """
        config = SynthesisConfig(length_scale=1.2)
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file, syn_config=config)
        return audio_buffer.getvalue()