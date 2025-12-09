import os
import itk
import logging
import argparse


from sci_segmentator.core.filters import itk_orient_image_to_axial


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
        type=str,
        action="store",
        required=True,
        help="Path to input image"
    )

    _ = parser.add_argument(
        "-tr",
        "--transform",
        dest="transforms",
        action="append",
        required=True,
        default=[],
        help=""
    )

    _ = parser.add_argument(
        "-out",
        "--output",
        dest="output",
        type=str,
        action="store",
        required=True,
        help=""
    )

    _ = parser.add_argument(
        "-b",
        "--binary",
        dest="binary",
        action="store_true",
        help="")

    _ = parser.add_argument(
        '-v',
        '--verbose',
        dest="verbose",
        action='count',
        default=0)

    args = parser.parse_args()
    return args


def run(image, transform, binary, n_transforms):

    logger.debug("Apply transforms")

    if binary:
        logger.debug("Set BSpline Interpolation ordere to zero")
        for idx in range(len(n_transforms)):
            _ = transform.SetParameter(idx, 'FinalBSplineInterpolationOrder', '0')

        logger.debing("Applying transforms to image")

        result = itk.transformix_filter(image, transform)
        return result

def main():
    
    args = parse_args()

    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    print(args)

    logger.info(f"Reading Image to transform from {args.input}")

    image = itk.imread(args.input, itk.F)
    image = itk_orient_image_to_axial(image)
    image = image.GetOutput()

    logger.info("Building transform object")

    transform = itk.ParameterObject.New()
    transform.ReadParameterFile(args.transforms)

    if args.binary:
        logging.info("Set BSPLine Interpolation ordere to zero")

        for idx in range(len(args.transforms)):
            _ = transform.SetParameter(idx, 'FinalBSplineInterpolationOrder', '0')

    logger.info("Applying transforms to image")

    result = itk.transformix_filter(image, transform)

    logger.info(f"Save result to {args.output}")

    itk.imwrite(result, args.output)



if __name__ == "__main__":
    main()