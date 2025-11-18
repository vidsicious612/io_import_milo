from dataclasses import dataclass

XMA_BITS_PER_SAMPLE = 16
XMA_BYTES_PER_PACKET = 2048
XMA_SAMPLES_PER_FRAME = 512

@dataclass
class XMA:
    data: bytes = ()
    sample_rate: int = 44100
    sample_count: int = 0
    
    def write(self, filepath: str):
        from .... writers import Writer

        with open(filepath, "wb") as f:
            writer = Writer(f)

            writer.utf8_string("RIFF")
            writer.int32(len(self.data) + 72)
            writer.utf8_string("WAVE")

            writer.utf8_string("fmt ")
            writer.int32(52)
            writer.short(358)
            writer.ushort(1)
            writer.uint32(self.sample_rate)
            writer.uint32(self.sample_rate)
            writer.ushort(2)
            writer.ushort(16)

            writer.ushort(34)
            writer.ushort(1)
            writer.uint32(4)
            writer.uint32(self.sample_count)
            writer.uint32(65536)
            writer.uint32(0)
            writer.uint32(self.sample_count)
            writer.uint32(0)
            writer.uint32(0)
            writer.ubyte(0)
            writer.ubyte(4)
            writer.ushort(len(self.data) // XMA_BYTES_PER_PACKET)

            writer.utf8_string("data")
            writer.int32(len(self.data))
            writer.write_bytes(self.data)

    def convert_with_vgmstream(self, input_file: str):
        import subprocess
        from pathlib import Path
        from .. audio_helpers.vgmstream_path import VGMSTREAM_PATH

        wav_path = Path(input_file).with_suffix(".wav")

        command = [str(VGMSTREAM_PATH), "-o", wav_path, input_file]

        subprocess.run(command)

        Path(input_file).unlink()