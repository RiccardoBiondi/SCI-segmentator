import os
import itk
import logging

from sci_segmentator.scripts import scan_ras_orienter
from sci_segmentator.scripts import bias_field_correction
from sci_segmentator.scripts import compute_head_region

def run(flair, t1):

    logger = logging.getLogger(__file__)
    logging.basicConfig(level=1)

    flair = scan_ras_orienter.run(flair, logger)
    t1 = scan_ras_orienter.run(t1, logger)

    #flair = bias_field_correction.run(flair.GetOutput(), logger)
    #t1 = bias_field_correction.run(t1.GetOutput(), logger)

    head = compute_head_region.run(t1.GetOutput(), logger)

    return "Fatto"
    
