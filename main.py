#!/bin/python3

from argparse import ArgumentParser
import os
from pathlib import Path
import subprocess
import re
import glob

RESOLUTION_REGEX = re.compile(r", (\d*)x(\d*), ")

ORIENTATION_UPPER = "orientation=upper-"
ORIENTATION_UPPER_RIGHT = "orientation=upper-right"
ORIENTATION_UPPER_LEFT = "orientation=upper-left"

def main():
    parser = ArgumentParser()

    parser.add_argument("path", type=str)

    args = parser.parse_args()
    path = Path(args.path)
    converted_dir = path.joinpath(Path("../converted"))

    converted_dir.mkdir(parents=True, exist_ok=True)

    files = os.listdir(path)
    
    len_files = len(files)
    for (idx, file) in enumerate(files):
        file = path.absolute().joinpath(file)
        filename = file.name

        converted_file = converted_dir.absolute().joinpath(filename)

        if converted_file.exists():
            continue

        file_info = subprocess.check_output(
            ["file", file.absolute()]).decode("utf-8")
        resolution_matches = RESOLUTION_REGEX.findall(file_info)

        if len(resolution_matches) != 1:
            continue

        resolution_match = resolution_matches[0]
        width = int(resolution_match[0])
        height = int(resolution_match[1])

        if (width > height and ORIENTATION_UPPER not in file_info) or (width > height and ORIENTATION_UPPER_LEFT in file_info) or (height > width and ORIENTATION_UPPER_RIGHT in file_info):
            print(f"Skipping landscape {file}")
            continue

        if ORIENTATION_UPPER_RIGHT in file_info:
            cmd = f"convert {file} -strip -rotate 90 {converted_file}"
            assert os.system(cmd) == 0, f"Cannot rotate image {file}"
            file = converted_file

            ratio = 1 + 1/3
            if width / height >= ratio:
                width = int(round(height * ratio, 0))

            width, height = height, width
        elif ORIENTATION_UPPER_LEFT in file_info:
            ratio = 1 + 1/3

            width, height = height, width

            if width / height >= ratio:
                width = int(round(height * ratio, 0))

            width, height = height, width


        cmd = f'convert -size {height}x{width} xc:skyblue {file} -geometry {height}x{width} -blur 0x25 -gravity northwest -composite {file} -geometry {height}x{width} -blur 0x25 -gravity southeast -composite {file} -geometry {height}x{width} -gravity center -composite {converted_file}'

        print(f"Converting ({idx+1}/{len_files}) {file}", end="", flush=True)
        assert os.system(cmd) == 0, f"Cannot converted image {file}"
        print(" OK")


if __name__ == "__main__":
    main()
