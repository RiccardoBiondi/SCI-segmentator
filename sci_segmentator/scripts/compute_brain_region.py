import os
import itk
import logging
import argparse
import numpy as np

from sci_segmentator.core.filters import itk_gaussian_normalization
from sci_segmentator.core.filters import itk_mask 
from sci_segmentator.core.filters import itk_binary_threshold
from sci_segmentator.core.filters import itk_multi_otsu_threshold
from sci_segmentator.core.filters import itk_binary_erode
from sci_segmentator.core.filters import itk_binary_dilate
from sci_segmentator.core.filters import itk_connected_components
from sci_segmentator.core.filters import itk_relabel_components
#from sci_segmentator.core.filters import here the hole filling import 

__author__ = ["Nicolas Biondini", "Riccardo Biondi"]
__email__ = ["nicolas.biondini2@unibo.it", "riccardo.biondi7@unibo.it"]

def parse_args():
    
    parser = argparse.ArgumentParser()

def run(image, initial_mask, logger = logging):

    # first of all binarize the input mask
    logger.debug("Prepre initial brain mask")
    first_mask = itk_binary_threshold(initial_mask, lower_thr=1, upper_thr=10)
    first_mask = itk_binary_dilate(first_mask.GetOutput(), radius=1)
    
    logger.debug("Apply Mask to T1 and normalize GL inside Brain")
    mask = itk_mask(image, first_mask.GetOutput())
    mask = itk_gaussian_normalization( image, mask.GetOutput())

    logger.debug("Extracting Brain Mask by Thhresholding")
    mask = itk_multi_otsu_threshold(mask.GetOutput(), number_of_thresholds=3)
    mask = itk_binary_threshold(mask.GetOutput(), lower_thr=1, upper_thr=3)

    logger.debug("Normalize secon tentative for brain mask")
    mask = itk_gaussian_normalization(image, mask.GetOutput())
    mask = itk_binary_threshold(mask.GetOutput(), lower_thr=-3, upper_thr=1.5)

    logger.debug("Determine the identified largest connected region") # forse meglio un'opening?
    mask = itk_binary_erode(mask.GetOutput(), radius=1)
    mask = itk_connected_components(mask.GetOutput())
    mask = itk_relabel_components(mask.GetOutput())
    mask = itk_binary_threshold(mask.GetOutput(), lower_thr=1, upper_thr=1)

    logger.debug("Fill Holes")

    


def main():
    ...

if __name__ == "__main__":
    main()