import os
import itk
import logging
import argparse

from sci_segmentator.core.filters import itk_orient_image_to_axial
from sci_segmentator.core.filters import itk_multi_otsu_threshold
from sci_segmentator.core.filters import itk_cast
from sci_segmentator.core.filters import itk_binary_morphological_closing
from sci_segmentator.core.filters import flood_fill_2d
from sci_segmentator.core.filters import itk_cast

LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


def parse_args():
    
    parser = argparse.ArgumentParser(description="Script to Identify the head region starting from the T1 weighted MRI")

    _ = parser.add_argument(
        "-in",
        "--input",
        dest="input",
        action="store",
        required=False,
        type=str,
        help="Path to the input MRI scan to correct. Input scan should be 2D or 3D and in .nii or .nii.gz format"
    )
    _ = parser.add_argument(
        "-out",
        "--output",
        dest="output",
        action="store",
        required=False,
        type=str,
        help="Path to save the resulting mask. Output scan format must be in .nii or .nii.gz"
    )

    #
    # Argument to control verbosity level
    #

    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)

    args = parser.parse_args()
    return args


def run(image, logger):

    _, dimension = itk.template(image)[1]

    if dimension not in [2, 3]:
        logger.error(f"Scan Dimension should be 2D or 3D, found {dimension}D instead")

    logger.info("Define the head region definition")
    brain = itk_multi_otsu_threshold(image,  1)
    brain = itk_cast(brain.GetOutput(), itk.SS)
    brain = itk_binary_morphological_closing(brain.GetOutput(), 5)
    brain = flood_fill_2d(brain.GetOutput())
    brain = itk_cast(brain.GetOutput(), itk.UC)
    
    return brain

def main():

    args = parse_args()

    logger = logging.getLogger(__file__)
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Reading scan from {args.input}")
    scan = itk.imread(args.input, itk.F)
    
    brain = run(scan, logger)

    logger.info(f"Writing the Results on {args.output}")

    _ = itk.imwrite(brain.GetOutput(), args.output)

if __name__ == "__main__":
    main()