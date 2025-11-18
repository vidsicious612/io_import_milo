from enum import Enum

class Platform(Enum):
    Gamecube = "gc"
    PC = "pc"
    PS2 = "ps2"
    PS3 = "ps3"
    Wii = "wii"
    X360 = "xbox"

def get_platform(filepath: str) -> Platform:
    if filepath.endswith("_gc"):
        return Platform.Gamecube
    elif filepath.endswith("_pc"):
        return Platform.PC
    elif (filepath.endswith(".rnd")) or (filepath.endswith("_ps2")):
        return Platform.PS2
    elif filepath.endswith("_ps3"):
        return Platform.PS3
    elif filepath.endswith("_wii"):
        return Platform.Wii
    elif filepath.endswith("_xbox"):
        return Platform.X360