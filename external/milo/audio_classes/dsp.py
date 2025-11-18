from dataclasses import dataclass, field

@dataclass
class DSP:
    data: memoryview = field(default_factory=memoryview)

    def write(self, filepath: str):
        from .... writers import Writer
        
        with open(filepath, "wb") as f:
            writer = Writer(f)
            writer.little_endian = False
            
            writer.write_bytes(self.data)        

    def convert_with_vgmstream(self, input_file: str):
        import subprocess
        from pathlib import Path
        from .. audio_helpers.vgmstream_path import VGMSTREAM_PATH

        wav_path = Path(input_file).with_suffix(".wav")

        command = [str(VGMSTREAM_PATH), "-o", wav_path, input_file]

        subprocess.run(command)

        Path(input_file).unlink()