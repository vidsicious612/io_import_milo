import platform

from pathlib import Path

if platform.system() == "Windows":
    VGMSTREAM_PATH = Path.joinpath(Path(__file__).parent.parent.parent, "vgmstream", "windows", "vgmstream-cli.exe")
elif platform.system() == "Darwin":
    VGMSTREAM_PATH = Path.joinpath(Path(__file__).parent.parent.parent, "vgmstream", "mac", "vgmstream-cli")
else:
    VGMSTREAM_PATH = Path.joinpath(Path(__file__).parent.parent.parent, "vgmstream", "linux", "vgmstream-cli")