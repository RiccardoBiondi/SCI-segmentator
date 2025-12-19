"""
Module to define the wrappiung of all the needed itk filters.
Those filters allows to pre and post process the images to segment.
Each filter is decorated by "update" decorator, which automatically uopdate the filter after the function call.
"""
import itk
import logging
import functools

__author__ = ["Riccardo Biondi", "Nicolas Biondini"]
__email__ = ["riccardo.biondi7@unibo.it", "nicolas.biondini2@unibo.it"]


__all__ = ["update", "infer_itk_image_type"]

logger = logging.getLogger(__file__)


def update(func):
    """
    Decorator to automatically update an itk pipeline. The pipeline must be
    initlaized with the input/s images as *args and other as kwargs.
    The pipeline must return an itk filter, not an image.

    To deactivate the usage of the dex  corator, simply specify: upadte=False
    as kwargs in the function.

    Example
    -------
    >>> import itk
    >>> from ipt.decorators import update
    >>>
    >>> # Create a decorated function containing the pipeline to update
    >>>
    >>> @update
    >>> def pipeline(image, radius=1, **kwargs):
    >>>   median_filter = itk.MedianImageFilter[type(image), type(image)].New()
    >>>   _ = median_filter.SetInput(image)
    >>>   _ = median_filter.SetRadius(radius)
    >>>
    >>>   return median_filter
    >>>
    >>> def main():
    >>>
    >>>   image = itk.imread('path/to/input/image')
    >>>   filtered = median_filter(image)
    >>>   _ = itk.imwrite('path/to/output', filtered.GetOutput())
    >>>
    >>> if __name__ == '__main__':
    >>>   main()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        pipeline = func(*args, **kwargs)

        if kwargs.get('update', True):
            logger.debug(f'Updating {func.__name__}')

            _ = pipeline.Update()

        return pipeline
    return wrapper


def infer_itk_image_type(image, desidered_type=None):
    '''
    Infer the desidered image type: if default type is None, will return the
    type of the specified image, otherwise will return desidered_type
s
    Parameters
    ----------
    image: itk.Image
        itk Image from which infer the type

    desidered_type: itk ImageType
        type to return instead of the one of image. Default: None

    Return
    ------
    image_type: itk Image type (i.e. itk.Image[itk.UC, 2])
        inferred image type
    '''
    logger.debug('Inferring image type')

    if desidered_type is not None:
        return desidered_type

    pixel_type, dimension = itk.template(image)[1]
    image_type = itk.Image[pixel_type, dimension]

    return image_type


@update
def itk_orient_image_to_axial(image, **kwargs):
    """
    Change the image orientation to axial one, closer to RIS
    """

    logger.debug('Orienting image to axial(RIS)')

    image_type = infer_itk_image_type(image)

    orienter = itk.OrientImageFilter[image_type, image_type].New()

    _ = orienter.UseImageDirectionOn()
    _ = orienter.SetDesiredCoordinateOrientationToAxial()
    _ = orienter.SetInput(image)

    return orienter


@update
def itk_binary_threshold(image, lower_thr=0, upper_thr=0, inside_value=1,
                        outside_value=0, input_type=None, output_type=None,
                         **kwargs):
    '''
    Apply a threshold in a specified interval and return a binary image. The
    values outside the inteval are setted to outside_value, the ones inside to
    inside_value.

    Parameters
    ----------
    image: itk.Image
        itk image to process
    lower_thr: PixelType
        lower threshold value
    upper_thr: PixelType
        upper threshold value
    inside_value: PixelType
        value to which set the voxels inside the specified inteval
    outside_value: PixelType
        value to which set the voxels outside the specified inteval
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        input image type. If not specified it is iferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators
    Return
    ------
    thr: itk.BinaryThresholdImageFilter
        New instance of binary threshold filter. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.
    '''

    logger.debug(f'Binary Threshold: -Upper thr: {upper_thr} - Lower \
    thr: {lower_thr}')

    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)

    thr = itk.BinaryThresholdImageFilter[
                                        input_image_type,
                                        output_image_type
                                        ].New()
    _ = thr.SetInput(image)
    _ = thr.SetLowerThreshold(lower_thr)
    _ = thr.SetUpperThreshold(upper_thr)
    _ = thr.SetInsideValue(inside_value)
    _ = thr.SetOutsideValue(outside_value)

    return thr


@update
def itk_change_information_from_reference(image,
                                        reference_image,
                                        change_direction=True,
                                        change_origin=True,
                                        change_spacing=True,
                                        change_region=True,
                                          input_type=None, **kwargs):
    '''
    Change the origin, spacing, direction and/or buffered region of an itkImage
    to the one of the specified reference image.

    Parameters
    ----------
    image: itk.Image
        input image
    reference_image: itk.Image
        reference image -> will be casted to the same type of input image
    change_direction: Bool
        Specify if change input image direction (default: True)
    change_origin: Bool
        Specify if change input image origin (default: True)
    change_spacing: Bool
        Specify if change input image spacing (default: True)
    change_region: Bool
        Specify if change input image region (default: True)
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        input image type. If not specified it is inferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    cahnger: itk.ChangeInformationImageFilter
        filter is updated by default.
        To not update the instance pecify update=False as kwargs.
    '''

    logger.debug(f'Change image information from reference.\
                    changing in formation targerts:  direction{change_direction}\
                    origin:{change_origin} spacing: {change_spacing} region: {change_region}')

    input_image_type = infer_itk_image_type(image, input_type)
    reference_image = itk.CastImageFilter[type(
        reference_image), input_image_type].New(reference_image)
    _ = reference_image.Update()
    changer = itk.ChangeInformationImageFilter[input_image_type].New()
    _ = changer.SetUseReferenceImage(True)
    _ = changer.SetInput(image)
    _ = changer.SetReferenceImage(reference_image.GetOutput())
    _ = changer.SetChangeDirection(change_direction)
    _ = changer.SetChangeOrigin(change_origin)
    _ = changer.SetChangeSpacing(change_spacing)
    _ = changer.SetChangeRegion(change_region)
    _ = changer.SetCenterImage(False)

    return changer


@update
def itk_mask(image, mask, masking_value=0, outside_value=0,
             input_type=None, mask_type=None, output_type=None, **kwargs):
    '''
    Mask an image with a binary mask. The image and the mask must
    be in the same physical space.

    Parameters
    ----------
    image : itk.Image
        image to mask
    mask : itk.Image
        binary mask
    masking_value : int
        label object ot mask
    outside_value : PixelType
        value to which set the voxels outside the mask
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        input image type. If not specified it is inferred from the input image
    mask_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        mask image type. If not specified it is iferred from the mask image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    masker : itk.MaskImageFilter
        mask image filter. As default the instance is updated.
        To not update the instance pecify update=False as kwargs.
    '''
    logger.debug('Masking the Image')

    input_image_type = infer_itk_image_type(image, input_type)
    mask_image_type = infer_itk_image_type(mask, mask_type)
    output_image_type = infer_itk_image_type(image, output_type)

    masker = itk.MaskImageFilter[input_image_type,
                                mask_image_type,
                                output_image_type
                                ].New()
    _ = masker.SetInput(image)
    _ = masker.SetMaskImage(mask)
    _ = masker.SetOutsideValue(outside_value)
    _ = masker.SetMaskingValue(masking_value)

    return masker


@update
def itk_label_statistics(image, labelmap, input_type=None, **kwargs):
    '''
    Given an intensity image and a label map, compute min, max, variance and
    mean of the pixels associated with each label or segment.

    Parameters
    ----------
    image: itk.Image
        intensity image
    labelmap: itk.LabelMap
        label map
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    filter_ : itk.LabelStatisticsImageFilter
        itk.LabelStatisticsImageFilter instance. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.
    '''

    logger.debug('Computing Lebel Statistics')
    input_image_type = infer_itk_image_type(image, input_type)

    # TODO Improve the type definition for the labelmap object
    filter_ = itk.LabelStatisticsImageFilter[
                                            input_image_type,
                                            type(labelmap)
                                            ].New()
    _ = filter_.SetLabelInput(labelmap)
    _ = filter_.SetInput(image)

    return filter_


@update
def itk_label_shape_statistics(image, label=1, input_type=None, **kwargs):

    pixel_type, dimension = itk.template(image)[1]
    input_type = itk.Image[pixel_type, dimension]

    ShapeLabelObjectType =  itk.StatisticsLabelObject[itk.UL, dimension]#itk.ShapeLabelObject[itk.UL, dimension]
    LabelMapType = itk.LabelMap[ShapeLabelObjectType]
    I2LType = itk.LabelImageToShapeLabelMapFilter[input_type, LabelMapType]
    i2l = I2LType.New()
    
    _ = i2l.SetInput(image)
    return i2l


@update
def itk_shift_scale(image, shift=0., scale=1.,
                    input_type=None, output_type=None, **kwargs):
    '''
    Shift and scale the pixels in an image.

    Parameters
    ----------
    image: itk.Image
        image to apply filter to
    shift: float
        shift factor
    scale: float
        scale factor
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    filter_ : itk.ShiftScaleImageFilter
        itk.ShiftScaleImageFilter instance. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.
    '''
    logger.debug(f'Shift and Scale: -shift: {shift} -scale: {scale}')

    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)

    filter_ = itk.ShiftScaleImageFilter[
                                        input_image_type,
                                        output_image_type
                                        ].New()
    _ = filter_.SetInput(image)
    _ = filter_.SetScale(scale)
    _ = filter_.SetShift(shift)

    return filter_


@update
def itk_gaussian_normalization(image, mask, label=1,
                               input_type=None, output_type=None, **kwargs):
    '''
    Normalize the datata according to mean and standard deviation of the
    voxels inside the specified mask image

    Parameters
    ----------
    image: itk.Image
        image to normalize
    mask: itk.Image
        ROI mask
    label: int
        label value to determine the ROI
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    '''

    # TODO imporve documentation
    logger.debug(f'Running Gaussian Normalization. ROI label={label}')

    stats = itk_label_statistics(image, mask,
                                input_type, update=kwargs.get('update', True))

    # TODO add standard values for the case in which the label filter is not
    # updated?? mbah
    shift = -stats.GetMean(label)
    scale = 1. / abs(stats.GetSigma(label))

    normalized = itk_shift_scale(
                                image, shift=shift, scale=scale,
                                input_type=input_type,
                                output_type=output_type,
                                update=kwargs.get('update', True))

    return normalized


def itk_constant_image_from_reference(reference_image, value=0):
    '''
    Create an image with constant voxel value. The image is created starting
    from a reference image

    Parameters
    ----------
    reference_image: itk.Image
        reference image: the output image will match the reference on all the
        physical properties.
    value: PixelType
        constant value of the image

    Return
    ------
    const : itk.Image
        constant image
    '''
    pixel_type, dimensions = itk.template(reference_image)[1]
    const = itk.Image[pixel_type, dimensions].New()
    _ = const.SetRegions(reference_image.GetLargestPossibleRegion())
    _ = const.Allocate()
    _ = const.FillBuffer(value)

    _ = const.SetSpacing(reference_image.GetSpacing())
    _ = const.SetDirection(reference_image.GetDirection())
    _ = const.SetOrigin(reference_image.GetOrigin())

    return const


@update
def itk_median(image, radius=1, input_type=None, output_type=None, **kwargs):
    '''
    Apply a median filter on the input image

    Parameters
    ----------
    image: itk.Image
        ima to apply filter to
    radius: int
        kernel radius
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        input image type. If not specified it is inferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators
    Results
    -------
    median: itk.MedianImageFilter
        itk.MedianImageFilter instance. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.
    '''
    logger.debug(f'Median Filter with Radius : {radius}')
    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)

    median = itk.MedianImageFilter[input_image_type, output_image_type].New()
    _ = median.SetInput(image)
    _ = median.SetRadius(radius)

    return median


@update
def itk_salt_and_pepper_noise(image, salt_value=1, pepper_value=0, prob=.05,
                              input_type=None, output_type=None, **kwargs):
    '''
    Apply Salt and Pepper Noise to an Image

    Parameters
    ----------
    image: itk.Image
        image to apply to SaltAndPepperNoise filter to.
    salt_value: pixel type
        saturated voxel value
    pepper_value: pixel type
        dead voxel value
    prob: float
        probability of noise event
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        input image type. If not specified it is inferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators
    Results
    -------
    filter: itk.SaltAndPepperNoiseImageFilter
        itk filter instance. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.
    '''
    logger.debug(f'Salt and Pepper Noise: Salt Value:\
    {salt_value} Pepper Value: {pepper_value} Noise Probability:\
    {prob}')

    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)

    filt = itk.SaltAndPepperNoiseImageFilter[input_image_type, output_image_type].New()
    _ = filt.SetInput(image)
    _ = filt.SetSaltValue(salt_value)
    _ = filt.SetPepperValue(pepper_value)
    _ = filt.SetProbability(prob)

    return filt


@update
def itk_connected_components(image, fully_connected=False, background_value=0,
                             input_type=None, output_type=None, **kwargs):
    '''
    Label the object of a binary image. Assign a Unique Label to each distinct
    object.

    Parameters
    ----------
    image: itk.Image
        binary image to process
    fully_connected: bool
        Set whether the connected components are defined strictly by face
        connectivity or by face+edge+vertex connectivity
    background_value: voxel type
        Set the pixel intensity to be used for background (non-object)
        regions of the image in the output
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        input image type. If not specified it is inferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
        output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    connected: itk.ConnectedComponentImageFilter
        itk.ConnectedComponentImageFilter instance. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.
    '''

    logger.debug(
        f'Computing Connected Components: - fully_connected: {fully_connected} - background_value: {background_value}')

    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)

    connected = itk.ConnectedComponentImageFilter[
                                                input_image_type,
                                                output_image_type].New()
    _ = connected.SetInput(image)
    _ = connected.SetFullyConnected(fully_connected)
    _ = connected.SetBackgroundValue(background_value)

    return connected


@update
def itk_voting_binary_iterative_hole_filling(
                                            image,
                                            radius=1,
                                            max_number_of_iterations=10,
                                            majority_threshold=1,
                                            foreground_value=1,
                                            background_value=0,
                                            input_type=None, **kwargs):
    '''
    Fills in holes and cavities by iteratively applying a voting operation.

    Parameters
    ----------
    image: itk.Image
        input binary image
    radius: int or list of int
        radius of the neighborhood used to compute the median
    max_number_of_iterations: int
        maximum number of iterations to perform
    majority_threshold: int
        number of pixels over 50% that will decide whether an OFF pixel will
        become ON or not
    foreground_value: int
        value associated with the Foreground(object) of the binary image
    background_value: int
        value associated with the Background of the binary image
    input_type: itk.Image type (i.e.itk.Image[itk.UC, 2])
         input image type. If not specified it is inferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    cahnger: itk.VotingBinaryIterativeHoleFillingImageFilter
        filter is updated by default.
        To not update the instance pecify update=False as kwargs.
    '''
    logger.debug(f'Voting Binary Hole filling: \
    majority_threshold={majority_threshold},\
    max_number_of_iterations={max_number_of_iterations},\
    foreground_value={foreground_value},\
    background_value={background_value},\
    radius={radius}')

    input_image_type = infer_itk_image_type(image, input_type)
    filter_ = itk.VotingBinaryIterativeHoleFillingImageFilter[input_image_type].New(
    )

    _ = filter_.SetInput(image)
    _ = filter_.SetMajorityThreshold(majority_threshold)
    _ = filter_.SetMaximumNumberOfIterations(max_number_of_iterations)
    _ = filter_.SetForegroundValue(foreground_value)
    _ = filter_.SetBackgroundValue(background_value)
    _ = filter_.SetRadius(radius)

    return filter_


@update
def itk_cast(image, new_type=itk.UC, **kwargs):
    '''
    Cast image voxel type to new_type. Preserve image dimensions

    Parameters
    ----------
    image: itk.Image
        Image to cast
    new_type: itk voxel type (i.e. itk.UC)
        new voxel type
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    cast: itk.CastImageFilter
        filter is updated by default.
        To not update the instance pecify update=False as kwargs.
    '''

    pixel_type, dimension = itk.template(image)[1]
    logger.debug(f'Casting image from {pixel_type} to {new_type}')
    input_image_type = itk.Image[pixel_type, dimension]
    output_image_type = itk.Image[new_type, dimension]

    cast = itk.CastImageFilter[input_image_type, output_image_type].New()
    _ = cast.SetInput(image)

    return cast


@update
def itk_n4_bias_field_correction(
                                image,
                                mask=None,
                                convergence_threshold=1e-4,
                                maximum_number_of_iterations=[50, 40, 30],
                                input_type=None,
                                mask_type=None,
                                output_type=None, **kwargs):
    """
    """
    logger.debug(f"N4 Bias Field Correction: - convergence threshold={convergence_threshold}  - maximum number of iterations={maximum_number_of_iterations}")
    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)
    _, dimension = itk.template(image)[1]
    mask_image_type = itk.Image[itk.UC, dimension]
    
    if mask is not None:
        mask_image_type = infer_itk_image_type(mask, mask_type)

    n_fitting_levels = len(maximum_number_of_iterations)
    filter_ = itk.N4BiasFieldCorrectionImageFilter[input_image_type, mask_image_type, output_image_type].New()
    _ = filter_.SetConvergenceThreshold(convergence_threshold)
    _ = filter_.SetMaximumNumberOfIterations(maximum_number_of_iterations)
    _ = filter_.SetNumberOfFittingLevels(n_fitting_levels)
    _ = filter_.SetInput1(image)

    if mask is not None:
        _ = filter_.SetInput2(mask)

    return filter_

@update
def itk_multi_otsu_threshold(image, number_of_thresholds=3, input_type=None, **kwargs):

    logger.debug(f"Multi Otsu Threshold: - number of thresholds={number_of_thresholds}")
    input_image_type = infer_itk_image_type(image, input_type)

    motsu = itk.OtsuMultipleThresholdsImageFilter[input_image_type, input_image_type].New()
    _ = motsu.SetInput(image)
    _ = motsu.SetNumberOfThresholds(number_of_thresholds)

    return motsu


@update
def itk_binary_morphological_closing(image, radius=1, foreground_value=1, input_type=None, **kwargs):

    logger.debug(f"Binary Morphological Closing: - radius={radius} - foreground_value={foreground_value} - structuring element=Ball")
    input_image_type = infer_itk_image_type(image, input_type)
    _, dimension = itk.template(image)[1]

    StructuringElementType = itk.FlatStructuringElement[dimension]
    structuring_element = StructuringElementType.Ball(radius)

    ClosingFilterType = itk.BinaryMorphologicalClosingImageFilter[input_image_type, input_image_type, StructuringElementType]
    closing = ClosingFilterType.New()
    closing.SetInput(image)
    closing.SetKernel(structuring_element)
    closing.SetForegroundValue(foreground_value)  # Intensity value to erode

    return closing


@update
def itk_add_images(image1, image2, input1_type=None, input2_type=None, output_type=None, **kwargs):
    """
    """

    logger.debug("Add Images")
    input1_image_type = infer_itk_image_type(image1, input1_type)
    input2_image_type = infer_itk_image_type(image2, input1_type)
    output_image_type = infer_itk_image_type(image1, output_type)


    add_image = itk.AddImageFilter[input1_image_type, input2_image_type, output_image_type].New()
    _ = add_image.SetInput1(image1)
    _ = add_image.SetInput2(image2)

    return add_image


@update
def itk_invert_intensity(image, maximum=1, input_type=None, output_type=None, **kwargs):
    """
    """

    logger.debug(f"Invert Intensity: maximum={maximum}")
    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)


    inverter = itk.InvertIntensityImageFilter[input_image_type, output_image_type].New()
    _ = inverter.SetInput(image)
    _ = inverter.SetMaximum(maximum)

    return inverter


@update
def itk_slice_by_slice(image, pipeline, slicing_dimension=2, **kwargs):

    logger.debug(f"Slice By Slice: slicing_dimension={slicing_dimension}")
    pixel_type, dimension = itk.template(image)[1]
    image_type = itk.Image[pixel_type, dimension]


    filter_ = itk.SliceBySliceImageFilter[image_type, image_type].New()
    _ = filter_.SetInput(image)
    _ = filter_.SetFilter(pipeline)
    _ = filter_.SetDimension(slicing_dimension)

    return filter_


@update
def flood_fill_2d(image, **kwargs):

    logger.debug("Fllod Fill 2d")

    PixelType, Dimension = itk.template(image)[1]

    invert = itk_invert_intensity(image)
    filled = itk.ConnectedComponentImageFilter[itk.Image[PixelType, 2], itk.Image[PixelType, 2]].New()

    filled = itk_slice_by_slice(invert.GetOutput(), filled)

    filled = itk_binary_threshold(filled.GetOutput(), upper_thr=700, lower_thr=2)

    filled = itk_add_images(filled.GetOutput(), image)

    return filled


@update
def itk_or(image1, image2, input1_type=None, input2_type=None, output_type=None, **kwargs):
    '''
    '''
    Input1Type = infer_itk_image_type(image1, input1_type)
    Input2Type = infer_itk_image_type(image2, input2_type)
    OutputType = infer_itk_image_type(image1, output_type)

    or_ = itk.OrImageFilter[Input1Type, Input2Type, OutputType].New()
    _ = or_.SetInput(0, image1)
    _ = or_.SetInput(1, image2)

    return or_


@update
def itk_region_of_interest(image, bbox, input_type=None, output_type=None):

    InputType = infer_itk_image_type(image, input_type)
    OutputType = infer_itk_image_type(image, output_type)

    filter_ = itk.RegionOfInterestImageFilter[InputType, OutputType].New()

    _ = filter_.SetInput(image)
    _ = filter_.SetRegionOfInterest(bbox)
    return filter_


@update
def itk_clamp(image, lower=0., upper=1., input_type=None, output_type=None, **kwargs):
    
    InputType = infer_itk_image_type(image, input_type)
    OutputType = infer_itk_image_type(image, output_type)

    filter_ = itk.ClampImageFilter[InputType, OutputType].New()
    _ = filter_.SetInput(image)
    _ = filter_.SetBounds(lower, upper)
    return filter_

@update
def itk_resample(
                        image,
                        new_size,
                        new_space,
                        interpolator,
                        out_value=0,
                        input_type=None,
                        output_type=None,
                        **kwargs):
    
    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)


    identity = itk.IdentityTransform[itk.D, 3].New()
    _ = identity.SetIdentity()
    
    resample_filter = itk.ResampleImageFilter[input_image_type, output_image_type].New()

    _ = resample_filter.SetTransform(identity)
    _ = resample_filter.SetInput(image)
    _ = resample_filter.SetSize(new_size)
    _ = resample_filter.SetOutputSpacing(new_space)
    _ = resample_filter.SetOutputOrigin(image.GetOrigin())
    _ = resample_filter.SetOutputDirection(image.GetDirection())
    _ = resample_filter.SetDefaultPixelValue(out_value)
    _ = resample_filter.SetInterpolator(interpolator)
    
    return resample_filter

@update
def itk_resample_onto_reference(
                        image,
                        reference,
                        interpolator,
                        out_value=0,
                        input_type=None,
                        output_type=None,
                        **kwargs):
    
    input_image_type = infer_itk_image_type(image, input_type)
    output_image_type = infer_itk_image_type(image, output_type)


    identity = itk.IdentityTransform[itk.D, 3].New()
    _ = identity.SetIdentity()
    
    resample_filter = itk.ResampleImageFilter[input_image_type, output_image_type].New()

    _ = resample_filter.SetTransform(identity)
    _ = resample_filter.SetInput(image)
    _ = resample_filter.SetUseReferenceImage(True)
    _ = resample_filter.SetReferenceImage(reference)
    _ = resample_filter.SetDefaultPixelValue(out_value)
    _ = resample_filter.SetInterpolator(interpolator)
    
    return resample_filter

@update
def itk_relabel_components(image,
                           sort_by_object_size=True,
                           minimum_object_size=None,
                           number_of_object_to_print=None,
                           input_type=None, output_type=None,
                           **kwargs):
    '''
    Relabel the components in an image such that consecutive labels are used.

    Parameters
    ----------
    image: itk.Image
        label image to relabel
    sort_by_object_size: bool
        specify if sort the object by their size
    minimum_object_size: int
        Set the minimum size in pixels for an object. All objects smaller than
        this size will be discarded and will not appear in the output label map
    number_of_object_to_print: int
        Set the number of objects enumerated and described when the filter is
        printed.
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         input image type. If not specified it is inferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Return
    ------
    relabeler: itk::RelabelComponentImageFilter
        itk::RelabelComponentImageFilter instance. As default the instance is
        updated. To not update the instance pecify update=False as kwargs.

    '''

    logging.debug(f'Relabel Components. - Sort by Size: {sort_by_object_size}  \
    - minimum size: {minimum_object_size} - number of objects to print: {number_of_object_to_print}')

    InputType = infer_itk_image_type(image, input_type)
    OutputType = infer_itk_image_type(image, output_type)

    relabeler = itk.RelabelComponentImageFilter[InputType, OutputType].New()
    _ = relabeler.SetInput(image)
    _ = relabeler.SetSortByObjectSize(sort_by_object_size)

    return relabeler

#
# Region Extraction

@update
def itk_binary_dilate(image, radius=1, foreground_value=1,
                      background_value=0, input_type=None, output_type=None,
                      **kwargs):
    '''
    Dilate a binary image using a ball kernel of the same dimension of the
    image volume.

    Parameters
    ----------
    image: itk.Image
        binary image to erode
    radius: int
        radius of the ball kernel
    foreground_value: voxel type
        Intensity value to erode
    background_value: voxel type
        Replacement Value
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         input image type. If not specified it is inferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Results
    -------
    dilate: itk.BinaryErodeImageFilter
        itk.BinaryErodeImageFilter instance. As default the instance is updated
        To not update the instance pecify update=False as kwargs.
    '''
    # TODO: add a way to chose the kind of structuring element
    _, dimension = itk.template(image)[1]
    InputType = infer_itk_image_type(image, input_type)
    OutputType = infer_itk_image_type(image, output_type)

    logging.debug(f'Binary Dilation with a Ball Kernel of \
                    Dimension {dimension} and Radius: {radius}')

    StructuringElementType = itk.FlatStructuringElement[dimension]
    structuring_element = StructuringElementType.Ball(radius)

    DilateFilterType = itk.BinaryDilateImageFilter[InputType, OutputType, StructuringElementType]
    dilate = DilateFilterType.New()
    dilate.SetInput(image)
    dilate.SetKernel(structuring_element)
    dilate.SetForegroundValue(foreground_value)  # Intensity value to erode
    dilate.SetBackgroundValue(background_value)  #

    return dilate

@update
def itk_binary_erode(image, radius=1, foreground_value=1,
                      background_value=0, input_type=None, output_type=None,
                      **kwargs):
    '''
    Erode a binary image using a ball kernel of the same dimension of the
    image volume.

    Parameters
    ----------
    image: itk.Image
        binary image to erode
    radius: int
        radius of the ball kernel
    foreground_value: voxel type
        Intensity value to erode
    background_value: voxel type
        Replacement Value
    input_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         input image type. If not specified it is inferred from the input image
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         output image type. If not specified it is iferred from the input image
    kwargs:
        keyword arguments to control the behaviour of deorators

    Results
    -------
    erode: itk.BinaryErodeImageFilter
        itk.BinaryErodeImageFilter instance. As default the instance is updated
        To not update the instance pecify update=False as kwargs.
    '''
    # TODO: add a way to chose the kind of structuring element
    _, dimension = itk.template(image)[1]
    InputType = infer_itk_image_type(image, input_type)
    OutputType = infer_itk_image_type(image, output_type)

    logging.debug(f'Binary Erosion with a Ball Kernel of \
                    Dimension {dimension} and Radius: {radius}')

    StructuringElementType = itk.FlatStructuringElement[dimension]
    structuring_element = StructuringElementType.Ball(radius)

    ErodeFilterType = itk.BinaryErodeImageFilter[InputType, OutputType, StructuringElementType]
    erode = ErodeFilterType.New()
    erode.SetInput(image)
    erode.SetKernel(structuring_element)
    erode.SetForegroundValue(foreground_value)  # Intensity value to erode
    erode.SetBackgroundValue(background_value)  #

    return erode


@update
def itk_subtract(
                image1, image2,
                input1_type=None,
                input2_type=None,
                output_type=None, **kwargs
                ):
    '''
    Subtract two itk images. Images must heve the same size and physical space.

    Parameters
    ----------
    image1: itk.Image
        first image to add
    image2: itk.Image
        second image to subtract
    input1_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         input1 type. If not specified it is inferred from the input image1
    input2_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         input2 type. If not specified it is inferred from the input image2
    output_type : itk.Image type (i.e.itk.Image[itk.UC, 2])
         output type. If not specified it is iferred from the input image2
    kwargs:
        keyword arguments to control the behaviour of deorators

    Results
    -------
    subtract_image: itk.SubtractImageFilter
        itk.SubtractImageFilter instance. As default the instance is updated.
        To not update the instance pecify update=False as kwargs.
    '''
    logging.debug('Subtract two Images')

    Input1Type = infer_itk_image_type(image1, input1_type)
    Input2Type = infer_itk_image_type(image2, input2_type)
    OutputType = infer_itk_image_type(image1, output_type)

    subtract_image = itk.SubtractImageFilter[Input1Type, Input2Type, OutputType].New()
    _ = subtract_image.SetInput1(image1)
    _ = subtract_image.SetInput2(image2)

    return subtract_image


@update
def itk_binary_fill_hole(image, foreground_value=1, fully_connected: bool = False, input_type=None, **kwargs):

    input_image_type = infer_itk_image_type(image, input_type)

    filter_ =  itk.BinaryFillholeImageFilter[input_image_type].New()
    _ = filter_.SetForegroundValue(foreground_value)
    _ = filter_.SetFullyConnected(fully_connected)
    _ = filter_.SetInput(image)

    return filter_
