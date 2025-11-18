import argparse

from .. external.milo.platform import get_platform
from .. external.milo.assets.bitmap import Bitmap
from readers import Reader

parser = argparse.ArgumentParser(description='A script that converts milo engine images to PNG.')

parser.add_argument("--input_file", type=str, required=True, help='Path to the input file.')
parser.add_argument("--output_file", type=str, required=True, help='Path to the output file.')

args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file

reader = Reader(open(input_file, "rb").read())

bitmap = Bitmap()
bitmap.read(reader)

platform = get_platform(input_file)

bitmap.convert(platform)
bitmap.export_to_image(output_file)

print(f"Successfully converted {input_file} to {output_file}!")