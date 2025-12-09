import os
import itk
import logging

from sci_segmentator.scripts import scan_ras_orienter
from sci_segmentator.scripts import bias_field_correction
from sci_segmentator.scripts import compute_head_region
from sci_segmentator.scripts import scan_registration
from sci_segmentator.scripts import apply_transforms

def run(flair, t1):

    logger = logging.getLogger(__file__)
    logging.basicConfig(level=1)

    flair = scan_ras_orienter.run(flair, logger)
    t1 = scan_ras_orienter.run(t1, logger)

    #flair = bias_field_correction.run(flair.GetOutput(), logger)
    #t1 = bias_field_correction.run(t1.GetOutput(), logger)

    head = compute_head_region.run(t1.GetOutput(), logger)

    # register t1 onto flair
    logger.info("Register T1 onto FLAIR")
    transform_params, parameter_maps, registered = scan_registration.run(moving=t1.GetOutput(), fixed=flair.GetOutput(), indirect=False, transforms=["rigid", "affine"], metrics="AdvancedMattesMutualInformation", resolutions=4, combination="Compose")

    logger.info("Register Head Mask onto FLAIR ")

    # apply transform onto exclusion region
    head = apply_transforms.run(head.GetOutput(), transform_params, True, 2)

    # apply transform onto exclusion region onto t1 to register onto FLAIR

    # map head region onto flair

    # get wm region from T1

    # 


    return head
    
