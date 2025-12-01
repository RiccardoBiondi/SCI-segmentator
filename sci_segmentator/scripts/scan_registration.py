import os
import itk
import logging
import argparse

from core.ragistration import get_multimap_parameters
from core.filters import itk_orient_image_to_axial
from core.filters import itk_multi_otsu_threshold
from core.filters import itk_cast

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
    parser = argparse.ArgumentParser(description="Script to Register the input image onto the reference one.")

    _ = parser.add_argument(
                            "-in",
                            "--input",
                            dest="input",
                            action="store",
                            type=str,
                            required=False,
                            help="Path to input image. Must be .nii or .nii.gz format")
    _ = parser.add_argument(
                            "-ref",
                            "--reference",
                            dest="reference",
                            action="store",
                            type=str,
                            required=False,
                            help="Path to the reference image. Must be in .nii or .nii.gz format"
    )

    #
    # Optional Output Arguments
    #

    _ = parser.add_argument(
                            "-out",
                            "--output",
                            dest="output",
                            action="store",
                            type=str,
                            required=False,
                            default=None,
                            help="Path to the output registered image, must nbe .nii or .nii.gz"
    )
    _ = parser.add_argument(
                            "-ot",
                            "--output_transform",
                            dest="output_transform",
                            action="store",
                            type=str,
                            required=False,
                            default=None,
                            help="Path to the output transform. Must be .txt file"
    )


    #
    # Here an important argument. It allows to chose if perfrom direct registration (i.e. input onto reference)
    # Or indiect one (reference onto input and then invert transforms)
    #
    _ = parser.add_argument(
                            "-i",
                            "--indirect",
                            dest="indirect",
                            action="store_true",
                            required=False,
                            help=""
    )
    #
    # Now the optional argumets to customize the registration process, i.e. 
    # transform selection, loss selection, etc.
    #
    _ = parser.add_argument(
                            "-t",
                            "--transform",
                            dest="transform",
                            action="append",
                            required=False,
                            default=[],
                            help="")
    _ = parser.add_argument(
                            "-r",
                            "--resolutions",
                            dest="resolutions",
                            action="store",
                            required=False,
                            default=4,
                            help="")
    _ = parser.add_argument(
                            "-m",
                            "--metric",
                            dest="metric",
                            action="store",
                            type=str,
                            required=False,
                            default= "AdvancedMattesMutualInformation")
    _ = parser.add_argument(
                            "-c",
                            "--combination",
                            dest="combination",
                            type=str,
                            required=False,
                            default="Compose")
    #
    # Finally arguments to control verbosity
    #
    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)

    args = parser.parse_args()
    return args


def indirect_registration(moving, fixed, modalities=["rigid", "affine"], metric="AdvancedMattesMutualInformation", resolutions=4, combine_parameters="Compose"):
    """
    """
    logger.debug(f"Indirect Registration: - modalities={modalities} - metric={metric} - resolutions={resolutions} - combine parameters={combine_parameters}")
    direct_parameter_map = get_multimap_parameters(metric=metric, resolutions=resolutions, modalities=modalities, transform_combination=combine_parameters, initial_tranform=False)
    indirect_parameter_map = get_multimap_parameters(metric='DisplacementMagnitudePenalty', resolutions=resolutions, modalities=modalities, transform_combination=combine_parameters, initial_tranform=True)

    _, direct_transform_parameters = itk.elastix_registration_method(moving, fixed,  parameter_object=direct_parameter_map, log_to_console=False)
    _, indirect_transform_parameters = itk.elastix_registration_method(fixed, fixed, parameter_object=indirect_parameter_map,  log_to_console=False, initial_transform_parameter_object=direct_transform_parameters)

    return indirect_transform_parameters, indirect_parameter_map


def direct_registration(moving, fixed, modalities=["rigid", "affine"], metric="AdvancedMattesMutualInformation", resolutions=4, combine_parameters="Compose"):

    parameter_map = get_multimap_parameters(metric=metric, resolutions=resolutions, modalities=modalities, transform_combination=combine_parameters, initial_tranform=False)

    _, transform_parameters = itk.elastix_registration_method(fixed, moving, parameter_object=parameter_map, log_to_console=False)
    return transform_parameters, parameter_map


def align_image_centroids(moving, fixed):

    # determine the image vector
    fixed_origin = [o for o in fixed.GetOrigin()]
    moving_origin = [o for o in moving.GetOrigin()]

    vector = [o1 - o2 for o1, o2 in zip(fixed_origin, moving_origin)]

    translation = itk.TranslationTransform[itk.D, 3].New()
    translation.Translate(vector)

    resampler = itk.ResampleImageFilter[itk.Image[itk.F, 3], itk.Image[itk.F, 3]].New()
    resampler.SetTransform(translation)
    resampler.SetInput(moving)
    resampler.SetSize(moving.GetLargestPossibleRegion().GetSize())

    resampler.Update()

    return resampler.GetOutput()


def run(moving, fixed, indirect, transforms, resolutions, metrics, combination, logger):

    if indirect:
        logger.info("Running Indirect Registration")        
        transform_params, transform_map = indirect_registration(moving, fixed, modalities=transforms, metric=metrics, resolutions=resolutions, combine_parameters=combination)

    else:
        logger.info("Rinning Registration")
        transform_params, transform_map = direct_registration(moving, fixed, modalities=transforms, metric=metrics, resolutions=resolutions, combine_parameters=combination)

    registered = itk.transformix_filter()
    if args.output_transform is not None:
        logger.info(f"Running Output Transforms with base name {args.output_transform}")
        for idx in range(transform_params.GetNumberOfParameterMaps()):
            parameter_map = transform_params.GetParameterMap(idx)
            transform_params.WriteParameterFile(parameter_map, f"{args.output_transform}_{idx}.txt" )
        # write the transform file

    if args.output is not None:
        logger.info("Appling estimated transforms to moving image ")
        registered =  itk.transformix_filter(moving, transform_params)
        logger.info(f"Writing resulting image to {args.output}")
        _ = itk.imwrite(registered, args.output)
    ...

def main():

    args = parse_args()


    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Reading input scan from {args.input}")
    moving = itk.imread(args.input, itk.F)
    moving = itk_orient_image_to_axial(moving)
    moving = moving.GetOutput() 
    logger.info(f"Reading reference scan from {args.reference}")
    fixed = itk.imread(args.reference, itk.F)

    if args.indirect:
        logger.info("Running Indirect Registration")        
        transform_params, transform_map = indirect_registration(moving, fixed, modalities=args.transform, metric=args.metric, resolutions=args.resolutions, combine_parameters=args.combination)

    else:
        logger.info("Rinning Registration")
        transform_params, transform_map = direct_registration(moving, fixed, modalities=args.transform, metric=args.metric, resolutions=args.resolutions, combine_parameters=args.combination)

    if args.output_transform is not None:
        logger.info(f"Running Output Transforms with base name {args.output_transform}")
        for idx in range(transform_params.GetNumberOfParameterMaps()):
            parameter_map = transform_params.GetParameterMap(idx)
            transform_params.WriteParameterFile(parameter_map, f"{args.output_transform}_{idx}.txt" )
        # write the transform file

    if args.output is not None:
        logger.info("Appling estimated transforms to moving image ")
        registered =  itk.transformix_filter(moving, transform_params)
        logger.info(f"Writing resulting image to {args.output}")
        _ = itk.imwrite(registered, args.output)


if __name__ == "__main__":
    main()