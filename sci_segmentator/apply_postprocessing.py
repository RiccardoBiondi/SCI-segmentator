import os
import itk
import logging
import argparse
import numpy as np
import pandas as pd

from core.filters import itk_resample
from core.filters import infer_itk_image_type
from core.filters import itk_binary_threshold
from core.filters import itk_connected_components
from core.filters import itk_relabel_components
from core.filters import itk_label_shape_statistics
from core.filters import itk_label_statistics
from core.filters import itk_cast
from core.filters import itk_binary_dilate
from core.filters import itk_subtract
from core.filters import itk_or


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
        "-ft",
        "--features",
        dest="features",
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
                            '-at',
                            '--activation_threshold',
                            dest='activation_threshold',
                            type=float,
                            action='store',
                            required=False,
                            default=.2)


    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)


    args = parser.parse_args()
    return args

def select_label(df, params):
    dt = df.loc[(df['lesion_volume_mm3'] > params[0]) & (df['lesion_volume_vx'] > params[1])]
    dt = dt.loc[((dt['exclusion_region_fraction'] < params[1]) | (dt['lesion_volume_mm3'] < params[2])) | (dt['lesion_volume_mm3'] >= params[2])]
    dt = dt.loc[dt['surrounding_wm_fraction'] > params[4]]
    
    return dt

def remove_false_positives(df,  lesion_volume=0., lesion_voxels=0., exclusion_volume=.5, exclusion_percentage=.5, wm_boundary_percentage=.5):
    
    #dt = df.loc[df.MaxFeterDiameter > 1.5]
    # make a first decision removing all the lesion that are unlikely to be so
    dt = df.loc[df["exclusion_region_fraction"] < .8] # remove all the lesions that are more than 80% inside the exclusion area
    dt = dt.loc[dt["surrounding_wm_fraction"] > .05] # remove all the lesions that are surrounded by less thant 5% of the white matter
    dt = dt.loc[(dt['lesion_volume_mm3'] > lesion_volume) & (dt['lesion_volume_vx'] > lesion_voxels)]
    dt = dt.loc[((dt['exclusion_region_fraction'] < exclusion_percentage) | (dt['lesion_volume_mm3'] < exclusion_volume)) | (dt['lesion_volume_mm3'] >= exclusion_volume)]
    dt = dt.loc[(dt['surrounding_wm_fraction'] > wm_boundary_percentage) | (dt["exclusion_region_fraction"] >= .1)]
    #dt = dt.loc[dt['surrounding_wm_fraction'] > .80]

    #dt = dt.loc[((dt['exclusion_region_fraction'] < exclusion_percentage) & (dt['lesion_volume_mm3'] < exclusion_volume)) | (dt['lesion_volume_mm3'] >= exclusion_volume)]
    #dt = dt.loc[((dt['surrounding_wm_fraction'] > wm_boundary_percentage) & (dt['exclusion_region_fraction'] < .1)) | (dt['exclusion_region_fraction'] >= .1)]
    
    return dt

def create_image(reference):
    
    region = itk.ImageRegion[3]()

    start = itk.Index[3]()
    _ = start.Fill(0)
    _ = region.SetIndex(start)
    _ = region.SetSize(reference.GetLargestPossibleRegion().GetSize())

    image = itk.Image[itk.UC, 3].New()
    _ = image.SetRegions(region)
    _ = image.Allocate()
    _ = image.FillBuffer(itk.NumericTraits[itk.UC].ZeroValue())

    _ = image.SetSpacing(reference.GetSpacing())
    _ = image.SetOrigin(reference.GetOrigin())
    _ = image.SetDirection(reference.GetDirection())

    return image


def main():
    args = parse_args()

    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info("Apply post processing")
    logger.info("Reading input activation map")
    image = itk.imread(args.input, itk.F)
    
    logger.info(f"Apply activation threshold of: {args.activation_threshold}")
    image = itk_binary_threshold(image, upper_thr=1.1, lower_thr=args.activation_threshold)
    logger.info("Identify all the unique lesions")
    image = itk_cast(image.GetOutput(), itk.SS)
    image = itk_connected_components(image.GetOutput(), fully_connected=True)
    image = itk_relabel_components(image.GetOutput())
    image = image.GetOutput()

    logger.info(f"Read Features From: {args.features}")
    df = pd.read_csv(args.features, sep=",")

    logger.info(f"Starting from {df.shape[0]} lesions")
    logger.info("Start Featrure Selection from lesion")
    df = remove_false_positives(df, lesion_volume=5.65, lesion_voxels=4, exclusion_volume=700, exclusion_percentage=0.30, wm_boundary_percentage=.8)
    logger.info(f"Selected {df.shape[0]} lesions")


    logger.info("Create the final image template")
    final = create_image(image)

    logger.info("Start lesion selection")

    for ls in df["lesion_id"].values:
        
        logger.info(f"Selecting lesion with id {ls}")
        lesion = itk_binary_threshold(image, lower_thr=int(ls), upper_thr=int(ls))
        lesion = itk_cast(lesion.GetOutput(), itk.UC)

        final = itk_or(final, lesion.GetOutput())
        final = final.GetOutput()

    logger.info(f"Writing result to {args.output}")

    itk.imwrite(final, args.output)

    #image_arr = 
    #final = np.zeros(pred_arr.shape, dtype=np.uint8)
    #final_lesions = data['LesionId'].values


    #for ls in final_lesions:

    #    final[pred_arr == ls] = 1

    #final = itk.GetImageFromArray(final)
    #_ = final.SetOrigin(pred.GetOutput().GetOrigin())
    #_ = final.SetSpacing(pred.GetOutput().GetSpacing())
    #_ = final.SetDirection(pred.GetOutput().GetDirection())


if __name__ == "__main__":
    main()