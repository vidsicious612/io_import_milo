import wave

from dataclasses import dataclass
from pathlib import Path

@dataclass
class WAV:
    channels: int = 1
    samp_width: int = 2
    sample_rate: int = 44100
    frames = None
    
    def read(self, filepath: Path):
        wav = wave.open(str(filepath), "rb")

        self.channels = wav.getnchannels()
        self.samp_width = wav.getsampwidth()
        self.sample_rate = wav.getframerate()
        self.frames = wav.readframes(wav.getnframes())

    def write(self, filepath: Path):
        wav = wave.open(str(filepath), "wb")

        wav.setnchannels(self.channels)
        wav.setsampwidth(self.samp_width)
        wav.setframerate(self.sample_rate)
        wav.writeframes(self.frames)