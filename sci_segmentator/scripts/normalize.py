import itk
import logging
import argparse

from core.filters import itk_label_statistics
from core.filters import itk_gaussian_normalization
from core.filters import itk_mask

__author__ = ["Riccardo Biondi", "Nicolas Biondini"]
__email__ = ["riccardo.biondi7@unibo.it", "nicolas.biondini2@unibo.it"]


LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

logger = logging.getLogger(__file__)


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

    logging.info("Normalizing GL in head region according mean and standard deviation inside the region itself")
    normalized = itk_gaussian_normalization(image=image, mask=mask)

    logging.info("Setting the values outside the mask region to the minimum GL value of the normalized region")

    stats = itk_label_statistics(image=normalized.GetOutput(), labelmap=mask)
    min_ = stats.GetMinimum(1)
    normalized = itk_mask(image=normalized.GetOutput(), mask=mask, outside_value=min_)

    logging.info(f"Saving the Result to {args.output}")
    itk.imwrite(normalized.GetOutput(), args.output)


if __name__ == "__main__":
    main()

