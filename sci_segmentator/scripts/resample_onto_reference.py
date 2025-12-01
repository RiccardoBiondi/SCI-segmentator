import os
import itk
import logging
import argparse

from core.filters import itk_resample_onto_reference
from core.filters import infer_itk_image_type
from core.filters import itk_clamp

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
        "-ref",
        "--reference",
        dest="reference",
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
    #
    # Optional Argumentss
    #
    _ = parser.add_argument(
                            '-i',
                            '--interpolator',
                            dest='interpolator',
                            type=str,
                            action='store',
                            required=False,
                            default='bspline')
    
    _ = parser.add_argument(
                            '-c',
                            '--clamp',
                            dest='clamp',
                            required=False,
                            action='store_true')

    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)


    args = parser.parse_args()
    return args


def itk_spline_interpolator(
                            input_type,
                            order = 3,
                            param_type = itk.D,
                            pixel_type = itk.F):
    interpolator = itk.BSplineInterpolateImageFunction[input_type, param_type, pixel_type].New()
    _ = interpolator.SetSplineOrder(order)
    
    return interpolator

def itk_nn_interpolator(
                        input_type,
                        coord_rep=itk.D):
    interpolator = itk.NearestNeighborInterpolateImageFunction[input_type, coord_rep].New() 
    
    return interpolator


INTERPOLATORS = {
    "nn": itk_nn_interpolator,
    "bspline": itk_spline_interpolator,
}

def main():


    args = parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Reading Image to Normalize from {args.input}")
    image = itk.imread(args.input, itk.F)
    input_type = infer_itk_image_type(image, None)

    logger.info(f"Reading reference image from {args.reference}")
    reference = itk.imread(args.reference, itk.F)

    logger.info(f"Init {args.interpolator} the interpolator")

    interpolator = INTERPOLATORS[args.interpolator](input_type)

    logger.info("Resample the image")
    resampled = itk_resample_onto_reference(image=image, reference=reference,  interpolator=interpolator)

    if args.clamp:
        logging.info("Clamp image in 0-1")
        resampled = itk_clamp(resampled.GetOutput())

    logging.info(f"Saving Image to {args.output}")
    itk.imwrite(resampled.GetOutput(), args.output)



    





if __name__ == "__main__":
    main()