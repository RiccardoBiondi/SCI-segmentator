import os
# Do not use GPU. That because tensorflow reserve all the ram for a single process, and with the snakemake file we want to run many process in parallel
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 
os.environ["KERAS_BACKEND"] = "tensorflow"

import itk
import logging
import argparse
import numpy as np
#import tensorflow as tf
#import tensorflow.keras as keras

from core.unet import get_base_model


__author__ = ['Riccardo Biondi']
__email__ = ['riccardo.biondi7@unibo.it']



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
                            action='store',
                            type=str,
                            required=True,
                            default=None)
    _ = parser.add_argument(
                            '-out',
                            '--output',
                            dest='output',
                            action='store',
                            type=str,
                            required=True,
                            default=None
    )
    _ = parser.add_argument(
                            '-w',
                            '--weights',
                            dest='weights',
                            action='store',
                            type=str,
                            required=True,
                            default=None)
    _ = parser.add_argument('-v', '--verbose', dest="verbose", action='count', default=0)
    args = parser.parse_args()

    return args 


def main():
    
    args = parse_args()
    logging.basicConfig(level=LOG_LEVELS[min(args.verbose, 3)])

    logger.info(f"Load the input image from {args.input}")

    image = itk.imread(args.input, itk.F)
    array = itk.GetArrayFromImage(image)

    logger.info(f"Init the UNet with pre-trained weights from {args.weights}")

    model = get_base_model((256, 256, 1), args.weights)

    logger.info(f"Run prediction on {array.shape[0]} images")

    pred = model.predict(array) 

    logger.info("Converting Prediction back to medical image")

    pred = pred.reshape(array.shape)

    # convert to itk image
    pred = itk.GetImageFromArray(pred)

    _ = pred.SetOrigin(image.GetOrigin())
    _ = pred.SetSpacing(image.GetSpacing())
    _ = pred.SetDirection(image.GetDirection())

    
    logging.info(f"Saving Image to {args.output}")
    itk.imwrite(pred, args.output)

if __name__ == "__main__":
    main()