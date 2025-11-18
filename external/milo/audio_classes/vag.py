from dataclasses import dataclass

@dataclass
class VAG:
    data: bytes = ()
    sample_rate: int = 44100
    
    def write(self, filepath: str):
        from .... writers import Writer
        
        with open(filepath, "wb") as f:
            writer = Writer(f)

            writer.little_endian = False

            writer.utf8_string("VAGp")
            writer.int32(32)
            writer.int32(0)
            writer.int32(len(self.data) + 16)
            writer.int32(self.sample_rate)
            writer.write_bytes(bytes([0] * 10))
            writer.byte(0)
            writer.byte(0)

            writer.utf8_string("                ")
            writer.write_bytes(bytes([0] * 16))
            
            writer.write_bytes(self.data)

    def convert_with_vgmstream(self, input_file: str):
        import subprocess
        from pathlib import Path
        from .. audio_helpers.vgmstream_path import VGMSTREAM_PATH

        wav_path = Path(input_file).with_suffix(".wav")

        command = [str(VGMSTREAM_PATH), "-o", wav_path, input_file]

        subprocess.run(command)

        Path(input_file).unlink()