import os
import itk
import argparse
import numpy as np
import pandas as pd

from sci_segmentator.core.filters import itk_connected_components
from sci_segmentator.core.filters import itk_relabel_components
from sci_segmentator.core.filters import itk_binary_threshold
from sci_segmentator.core.filters import itk_cast

from typing import Dict, List, Tuple, NoReturn, Any, Optional


def parse_args():
    ...


def run(segmentation: itk.Image, arterial_atlas: itk.Image, brain_region: itk.Image, wm_region: itk.Image) -> Dict[str, float]:
    
    # first of all, retrieve the number of lesions and the total lesion burder
    seg = itk_cast(segmentation, itk.SS)
    connected  = itk_connected_components(seg.GetOutput(), fully_connected=True)
    spacing = segmentation.GetSpacing()
    vx_volume = spacing[0] * spacing[1] * spacing[2]

    seg_arr = itk.GetArrayFromImage(segmentation)
    brain_arr = itk.GetArrayFromImage(brain_region)
    wm_arr = itk.GetArrayFromImage(wm_region)
    arterial_arr = itk.GetArrayFromImage(arterial_atlas)
    connected_arr = itk.GetArrayFromImage(connected.GetOutput())

    aca_lesions = np.unique(connected_arr[arterial_arr == 1]).shape[0] - 1
    mca_lesions = np.unique(connected_arr[arterial_arr == 2]).shape[0] - 1
    pca_lesions = np.unique(connected_arr[arterial_arr == 3]).shape[0] - 1


    return {
        "NumberOfLesions": connected.GetObjectCount(),
        "LesionBurden": np.sum(seg_arr) * vx_volume,
        "BrainInvolvment": np.sum(seg_arr) / np.sum(brain_arr),
        "WhiteMatterInvolvment": np.sum(seg_arr) / np.sum(wm_arr),
        "ACAInvolvment": np.sum(seg_arr[arterial_arr == 1]) / np.sum((arterial_arr == 1).astype(np.uint8)),
        "MCAInvolvment": np.sum(seg_arr[arterial_arr == 2]) / np.sum((arterial_arr == 2).astype(np.uint8)),
        "PCAInvolvment": np.sum(seg_arr[arterial_arr == 3]) / np.sum((arterial_arr == 3).astype(np.uint8)),
        "ACALesions": aca_lesions,
        "MCALesions": mca_lesions,
        "PCALesions": pca_lesions
    }
    