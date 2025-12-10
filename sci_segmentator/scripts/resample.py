import os
import itk
import logging
import argparse

from sci_segmentator.core.filters import itk_resample
from sci_segmentator.core.filters import infer_itk_image_type


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
                            type=bool,
                            required=False,
                            default=False,
                            action='store')

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


def run(image, interpolator="nn", logger=logging):
    input_type = infer_itk_image_type(image, None)

    logger.debug(f"Computing the new image spacing, for the size of 256 256 in sagittal and coronal directions")

    logger.debug(f"Image Size {image.GetLargestPossibleRegion().GetSize()}")
    logger.debug(f"Image Spacing {image.GetSpacing()}")

    old_size = image.GetLargestPossibleRegion().GetSize()
    old_space = image.GetSpacing()
    new_size = [256, 256, image.GetLargestPossibleRegion().GetSize()[2]]
    new_space = [o_sp * o_sz / n_sz for o_sp, o_sz, n_sz in zip(old_space, old_size, new_size)]
    
    logger.debug(f"New Image Size {new_size}")
    logger.debug(f"New Image Spacing {new_space}")

    logger.debug(f"Init {interpolator} the interpolator")

    interpolator = INTERPOLATORS[interpolator](input_type)

    logger.debug("Resample the image")
    resampled = itk_resample(image=image, new_size=new_size, new_space=new_space, interpolator=interpolator)

    return resampled

def main():


    args = parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Reading Image to Normalize from {args.input}")
    image = itk.imread(args.input, itk.F)
 
    resampled = run(image, args.interpolator, logger)
    logging.info(f"Saving Image to {args.output}")
    itk.imwrite(resampled.GetOutput(), args.output)



    





if __name__ == "__main__":
    main()