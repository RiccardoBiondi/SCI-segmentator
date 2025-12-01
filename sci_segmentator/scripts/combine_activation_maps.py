import os
import itk
import logging
import argparse
import numpy as np

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
                            '-am',
                            '--activation_map',
                            dest='activation_maps',
                            type=str,
                            action='append',
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

    logger.info("Reading input activation maps")

    print(args.activation_maps)

    maps = [itk.imread(path, itk.F) for path in args.activation_maps]
    arrs = np.asarray([itk.GetArrayFromImage(map_) for map_ in maps])
    arrs = np.mean(arrs, axis=0)
    img = itk.GetImageFromArray(arrs)
    _ = img.SetSpacing(maps[0].GetSpacing())
    _ = img.SetOrigin(maps[0].GetOrigin())
    _ = img.SetDirection(maps[0].GetDirection())

    _ = itk.imwrite(img, args.output)


if __name__ == '__main__':
    main()
