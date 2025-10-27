import os
import logging
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# import of custom function and files
from sci_segmentator.core.utils import _get_gpu_report
from sci_segmentator.core.feeder import ImageFeeder

def parse_args():

    parser = argparse.ArgumentParser()
    _ = parser.add_argument(
                            '--datafile',
                            dest='datafile',
                            type=str,
                            action='store',
                            required=False,
                            default=None)

    _ = parser.add_argument(
                            '--image_path',
                            dest='image_path',
                            type=str,
                            action='store',
                            required=False,
                            default=None)
    _ = parser.add_argument(
                            '--wpath',
                            dest='wpath',
                            type=str,
                            action='store',
                            required=False,
                            default=None)
    _ = parser.add_argument(
                            '--output',
                            dest='output',
                            type=str,
                            action='store',
                            required=False,
                            default=None)
    _ = parser.add_argument(
                            '--batch',
                            dest='batch',
                            type=int,
                            action='store',
                            required=False,
                            default=8)
    _ = parser.add_argument(
                            '--epochs',
                            dest='epochs',
                            type=int,
                            action='store',
                            required=False,
                            default=200)
    _ = parser.add_argument(
                            '--lr',
                            dest='lr',
                            type=float,
                            action='store',
                            required=False,
                            default=1e-3)

    _ = parser.add_argument(
                            '--tfraction',
                            dest='tfraction',
                            type=float,
                            required=False,
                            action='store',
                            default=.7)

    _ = parser.add_argument(
                            '--project',
                            dest='project',
                            type=str,
                            action='store',
                            required=False,
                            default="sickle-cell")
    
    _ = parser.add_argument(
                            '--volume_thr',
                            dest='volume_threshold',
                            type=float,
                            action='store',
                            required=False,
                            default=4.)
    args = parser.parse_args()

    return args


def main():
    
    print("Start training of SCI-segmentation ensamble elements")
    print(_get_gpu_report())

    args = parse_args()
    config = {
        "epochs": args.epochs,
        "batch_size": args.batch,
        "learning_rate": args.lr,
        "volume_thr": args.volume_threshold,
        "starting_model": args.wpath
    }

    print("Training configuration:")
    for k, v in config.items():
        print(f"\t {k}: {v}")


if __name__ == "__main__":
    main()