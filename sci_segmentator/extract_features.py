import os
import itk
import logging
import argparse
import numpy as np
import pandas as pd

from core.filters import itk_binary_threshold
from core.filters import itk_connected_components
from core.filters import itk_relabel_components
from core.filters import itk_label_shape_statistics
from core.filters import itk_label_statistics
from core.filters import itk_cast
from core.filters import itk_binary_dilate
from core.filters import itk_subtract

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
        "-ex",
        "--exclusion",
        dest="exclusion",
        action="store",
        type=str,
        required=True,
        help=""
    )


    _ = parser.add_argument(
        "-wm",
        "--white_matter",
        dest="white_matter",
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

    _ = parser.add_argument(
        "-at",
        "--activation_threshold",
        dest="activation_threshold",
        action="store",
        type=float,
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

def main():


    args = parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Reading Input Image{args.input}")
    image = itk.imread(args.input, itk.F)

    logger.info(f"Reading Exclusion Region Image{args.exclusion}")
    exclusion = itk.imread(args.exclusion, itk.F)

    logger.info(f"Reading White Matter {args.white_matter}")
    white_matter = itk.imread(args.white_matter, itk.F)

    logger.info("Apply activation threshold")
    image = itk_binary_threshold(image, upper_thr=1.1, lower_thr=args.activation_threshold)
    logger.info("Identify all the unique lesions")
    image = itk_cast(image.GetOutput(), itk.SS)
    image = itk_connected_components(image.GetOutput(), fully_connected=True)
    image = itk_relabel_components(image.GetOutput())

    logger.info("Estimating Lesion Volume")
    physical_size = image.GetSizeOfObjectsInPhysicalUnits()
    number_of_voxels = image.GetSizeOfObjectsInPixels()
    label_idxs = np.arange(1, image.GetNumberOfObjects() + 1)


    # compute border image

    border = image.GetOutput()

    for i in label_idxs:
        border = itk_binary_dilate(border, foreground_value=int(i))
        border = border.GetOutput()

    border = itk_subtract(border, image.GetOutput())

    logger.info("Estimating White Matter Fraction")

    wm_stats = itk_label_statistics(white_matter, border.GetOutput())
    wm_fraction = [wm_stats.GetMean(int(i)) for i in label_idxs]
    

    logger.info("Estimating Exclusion Region Fraction")
    ex_stats = itk_label_statistics(exclusion, image.GetOutput())
    ex_fraction = [ex_stats.GetMean(int(i)) for i in label_idxs]
    
    logger.info("Creating the Features dataset")

    df = pd.DataFrame(data={
        "lesion_id": label_idxs,
        "lesion_volume_mm3": physical_size,
        "lesion_volume_vx": number_of_voxels,
        "surrounding_wm_fraction": wm_fraction,
        "exclusion_region_fraction": ex_fraction
    })

    logger.info(f"Writing features to {args.output}")
    df.to_csv(args.output, sep=",", index=None)


    





if __name__ == "__main__":
    main()