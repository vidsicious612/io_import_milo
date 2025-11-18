from dataclasses import dataclass

@dataclass
class VGS:
    def convert_with_vgmstream(self, input_file: str):
        import subprocess
        from .. audio_helpers.vgmstream_path import VGMSTREAM_PATH
        
        wav_path = input_file.replace(".vgs", ".wav")

        command = [str(VGMSTREAM_PATH), "-o", wav_path, input_file]

        subprocess.run(command)