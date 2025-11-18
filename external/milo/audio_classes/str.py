from dataclasses import dataclass, field

STR_INTERLEAVE_SIZE = 512
STR_CHANNELS = 2

class STR:
    data: memoryview = field(default_factory=memoryview)
    decoded_audio: bytearray = field(default_factory=bytearray)

    def convert(self):
        self.deinterleave()
        self.convert_to_samples()

    def deinterleave(self):
        buffer = bytearray([0] * (STR_INTERLEAVE_SIZE * STR_CHANNELS))

        for i in range(0, len(self.data), STR_INTERLEAVE_SIZE * STR_CHANNELS):
            chunk = self.data[i:i + (STR_INTERLEAVE_SIZE * STR_CHANNELS)]

            half_size = len(chunk) // 2

            for j, d in enumerate(chunk[:half_size]):
                buffer[((j >> 1) * 4) + (j & 1)] = d

            for j, d in enumerate(chunk[half_size:]):
                buffer[((j >> 1) * 4) + (j & 1) + 2] = d

            self.decoded_audio[i:i + (STR_INTERLEAVE_SIZE * STR_CHANNELS)] = buffer[:len(chunk)]

    def convert_to_samples(self):
        samples = [0] * (len(self.data) // 2)

        for i in range(0, len(self.data), 2):
            samples[i // 2] = self.data[i:i + 2]

        for i in range(len(samples)):
            if not isinstance(samples[i], bytes):
                samples[i] = bytes(samples[i])

        self.decoded_audio = b"".join(samples)

    def to_wav(self, filepath: str):
        import wave

        wav = wave.open(str(filepath, "wb"))
        
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(self.decoded_audio)