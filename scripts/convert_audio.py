import argparse

from .. external.milo.audio_classes.str import STR
from .. external.milo.audio_classes.vgs import VGS
from .. external.milo.assets.sample_data import SampleData
from readers import Reader

parser = argparse.ArgumentParser(description='A script that converts milo engine audio to WAV.')

parser.add_argument("--input_file", type=str, required=True, help='Path to the input file.')
parser.add_argument("--output_file", type=str, required=True, help='Path to the output file.')

args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file

if input_file.endswith(".str"):
    str = STR(data=open(input_file, "rb").read())
    str.convert()
    str.to_wav(output_file)
elif input_file.endswith(".vgs"):
    vgs = VGS()
    vgs.convert_with_vgmstream(input_file)
else:
    reader = Reader(open(input_file, "rb").read())

    sample_data = SampleData()
    sample_data.read(reader)
    sample_data.convert(output_file)

print(f"Successfully converted {input_file} to {output_file}!")