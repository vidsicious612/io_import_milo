from dataclasses import dataclass, field
from enum import Enum

class Encoding(Enum):
    kPCM = 0
    kBigEndianPCM = 1
    kVAG = 2
    kXMA = 3
    kATRAC = 4
    kMSF = 5
    kNintendoADPCM = 6

@dataclass
class SampleMarker:
    name: str = ""
    sample: int = 0
    
    def read(self, reader):
        self.name = reader.numstring()
        self.sample = reader.int32()
    
    def write(self, writer):
        writer.numstring(self.name)
        writer.int32(self.sample)

@dataclass
class SampleData:
    version: int = 0
    encoding: Encoding = Encoding.kPCM
    sample_count: int = 0
    sample_rate: int = 44100
    sample_size: int = 0
    read_samples: bool = True
    samples: bytes = ()
    sample_markers: list[SampleMarker] = field(default_factory=list)

    def read(self, reader):
        self.version = reader.int32()

        if self.version == 16:
            unknown = reader.uint32()

        self.encoding = Encoding(reader.int32())

        self.sample_count = reader.int32()
        self.sample_rate = reader.int32()
        self.sample_size = reader.int32()

        self.read_samples = reader.milo_bool()

        if self.read_samples == True:
            self.samples = reader.read_bytes(self.sample_size)

        if self.version >= 14:
            marker_count = reader.int32()

            for _ in range(marker_count):
                marker = SampleMarker()
                marker.read(reader)

                self.sample_markers.append(marker)

    def write(self, writer):
        writer.int32(self.version)

        writer.int32(self.encoding.value)

        writer.int32(self.sample_count)
        writer.int32(self.sample_rate)
        writer.int32(self.sample_size)

        writer.milo_bool(self.read_samples)

        writer.write_bytes(self.audio_data)
     
    def convert(self, filepath: str):
        from pathlib import Path
        from .. audio_classes.dsp import DSP
        from .. audio_classes.msf import MSF
        from .. audio_classes.vag import VAG
        from .. audio_classes.wav import WAV
        from .. audio_classes.xma import XMA

        if (self.encoding == Encoding.kPCM) or (self.encoding == Encoding.kBigEndianPCM):
            wav = WAV(sample_rate=self.sample_rate)

            wav.write(Path(filepath).with_suffix(".wav"))
        if self.encoding == Encoding.kVAG:
            vag = VAG(data=self.samples, sample_rate=self.sample_rate)

            vag.write(Path(filepath).with_suffix(".vag"))
            vag.convert_with_vgmstream(Path(filepath).with_suffix(".vag"))
        elif self.encoding == Encoding.kXMA:
            xma = XMA(data=self.samples, sample_rate=self.sample_rate, sample_count=self.sample_count)

            xma.write(Path(filepath).with_suffix(".xma"))
            xma.convert_with_vgmstream(Path(filepath).with_suffix(".xma"))
        elif self.encoding == Encoding.kMSF:
            msf = MSF(data=self.samples)

            msf.write(Path(filepath).with_suffix(".msf"))
            msf.convert_with_vgmstream(Path(filepath).with_suffix(".msf"))
        elif self.encoding == Encoding.kNintendoADPCM:
            dsp = DSP(data=self.samples)
            
            dsp.write(Path(filepath).with_suffix(".dsp"))
            dsp.convert_with_vgmstream(Path(filepath).with_suffix(".dsp"))