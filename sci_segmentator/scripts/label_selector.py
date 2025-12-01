import os
import itk
import logging
import argparse
import numpy as np

from core.filters import itk_binary_threshold
from core.filters import itk_or

LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}

logger = logging.getLogger(__file__)


def parse_args():
    
    parser = argparse.ArgumentParser()
    _ = parser.add_argument(
                            '-in',
                            '--input',
                            dest='input',
                            type=str,
                            action='store',
                            required=True,
                            default=None)
    _ = parser.add_argument(
                            '-out',
                            '--output',
                            dest='output',
                            type=str,
                            action='store',
                            required=True,
                            default=None)
    
    _ = parser.add_argument(
                            '-lb',
                            '--label',
                            dest='labels',
                            action='append',
                            type=int,
                            required=True,
                            default=None)
    _ = parser.add_argument(
                            '-v',
                            '--verbose',
                            dest="verbose",
                            action='count',
                            default=0)
    
    args = parser.parse_args()
    return args

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

    labelmap = itk.imread(args.input, itk.UC)
    mask =  create_image(labelmap)

    for label in args.labels:

        # threshold the labelmap
        thr = itk_binary_threshold(labelmap, lower_thr=label, upper_thr=label)
        thr = thr.GetOutput()

        # and combine to the output mask
        mask = itk_or(mask, thr)
        mask = mask.GetOutput()

        itk.imwrite(mask, args.output)

if __name__ == '__main__':
    main()
