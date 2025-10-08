import os
import itk
import logging
import argparse

from core.filters import itk_label_shape_statistics
from core.filters import itk_region_of_interest


LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

logger = logging.getLogger(__file__)

TYPES = {
        'int': itk.UC,
        'float': itk.F}

INTERPOLATORS = {
                'int': 'nn',
                'float': 'bspline'}

TYPE_CAST = {
            'int': int,
            'float': float
}

def parse_args():
    
    parser = argparse.ArgumentParser(description="")

    _ = parser.add_argument(
        "-in",
        "--input",
        dest="input",
        action="store",
        type=str,
        required=True,
        help=""
    )
    _ = parser.add_argument(
        "-ms",
        "--mask",
        dest="mask",
        action="store",
        type=str,
        required=True,
        help=""
    )
    _ = parser.add_argument(
        "-out",
        "--output",
        dest="output",
        action="store",
        type=str,
        required=True,
        help=""
    )

    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)


    args = parser.parse_args()
    return args


def main():
    
    args = parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Reading Image to Normalize from {args.input}")
    image = itk.imread(args.input, itk.F)

    logger.info(f"Reading Region Mask from {args.mask}")
    mask = itk.imread(args.mask, itk.UC)

    logger.info("Get Boiunding Box containing the head")
    stats = itk_label_shape_statistics(mask, label=1)
    bbox = stats.GetOutput().GetNthLabelObject(0).GetBoundingBox()

    logger.info("Cropping the target image")
    res = itk_region_of_interest(image, bbox)

    logger.info(f"Saving the Result to {args.output}")
    itk.imwrite(res.GetOutput(), args.output)



if __name__ == "__main__":
    main()