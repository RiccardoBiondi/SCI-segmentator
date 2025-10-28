import os
import shutil
import logging
import argparse
from urllib.request import urlretrieve

__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]

LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

logger = logging.getLogger(__file__)

LUT = {
    "ensamble_0.h5": "https://zenodo.org/records/17292493/files/ensamble_0.h5",
    "ensamble_1.h5": "https://zenodo.org/records/17292493/files/ensamble_1.h5",
    "ensamble_2.h5": "https://zenodo.org/records/17292493/files/ensamble_2.h5",
    "ensamble_3.h5": "https://zenodo.org/records/17292493/files/ensamble_3.h5",
    "ensamble_4.h5": "https://zenodo.org/records/17292493/files/ensamble_4.h5",
    "MNI152_Exclusion_Region.nii": "https://zenodo.org/records/17292493/files/MNI152_Exclusion_Region.nii",
    "MNI152_T1_1mm.nii.gz": "https://zenodo.org/records/17292493/files/MNI152_T1_1mm.nii.gz"}

def parse_args():
    
    parser = argparse.ArgumentParser(description="Downloader of the model fixtures")
    _ = parser.add_argument(
                            "-dst",
                            "--dest",
                            dest="dest",
                            action="store",
                            required=False,
                            default=None,
                            help="Fixture destination folder")
    
    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)

    args = parser.parse_args()
    return args

def main():

    args = parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info("Start Fixture Downloadiong")

    if args.dest is not None:
        logger.info(f"Specified destination folder: {args.dest}")
        destination_folder = args.dest

    else:
        destination_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
        logger.info(f"No destination folder specifying, using the defautl one: {destination_folder}")

    for k, v in LUT.items():
        output = os.path.join(destination_folder, k)
        logger.info(f"Downloading {k} in {output}")
        urlretrieve(v, output)


if __name__ == "__main__":
    main()