import os
import cv2
import logging
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
import albumentations as A
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# import of custom function and files
from sci_segmentator.core.utils import _get_gpu_report
from sci_segmentator.core.feeder import ImageFeeder
from sci_segmentator.core.losses import tversky_loss, dice_coeff
from sci_segmentator.core.augmentation import DataAugmentation

from datetime import datetime


LOG_LEVELS = {
    0: logging.ERROR,
    1: logging.WARN,
    2: logging.INFO,
    3: logging.DEBUG,
}

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


    # todo: add image size argument
    # todo: add accelerator control argument
    # todo: add random seed selector
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
        "starting_model": args.wpath,
        "image_path": args.image_path,
        "training dataset fraction": args.tfraction
    }

    # setting log level to control output verbosity
    log_level = LOG_LEVELS[2]#[min(args.verbosity, max(log_levels.keys()))]
    log_format = '%(asctime)s - %(name)s -  %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    print("Training configuration:")
    for k, v in config.items():
        print(f"\t {k}: {v}")

    #
    # Now I have to prepare the training
    # the training 
    #
    logging.info(f"Reading Slice Database from {args.datafile}")
    df = pd.read_csv(args.datafile, sep=",", index_col=False)
    nslices = df.shape[0]
    logging.info(f"Filtering out all the images wil a lesion burden less of {args.volume_threshold} Voxels")
    df = df.loc[df['Volume(#Voxels)'] > args.volume_threshold]
    fslices = df.shape[0]
    logging.info(f"Selected {fslices} out of {nslices} total")

    print("Creating Train and Validation Image Feeder")
    unique_partecipants = df.PartecipantId.unique()
    _ = np.random.shuffle(unique_partecipants)
    logging.info(f"Found {len(unique_partecipants)} unique partecipants")
    tindex = np.round(args.tfraction * len(unique_partecipants))
    TRAIN_PATIENTIS = unique_partecipants[:tindex]
    VAL_PATIENTS = unique_partecipants[tindex:]
    train_imgs = df.loc[df.PartecipantId.isin(TRAIN_PATIENTIS)].ImageName.values
    val_imgs = df.loc[df.PartecipantId.isin(VAL_PATIENTIS)].ImageName.values

    train_img_paths = list(map(lambda x: os.path.join(args.image_path, 'flair', f'{x}.nii.gz'), train_imgs))#, os.path.join(args.image_path, 't1_75', f'{x}.nii')], train_imgs))
    train_lab_paths = list(map(lambda x: os.path.join(args.image_path, 'labels', f'{x}.nii.gz'), train_imgs))
    logging.info(f"Found a total of {len(train_img_paths)} training images")

    val_img_paths = list(map(lambda x: os.path.join(args.image_path, 'flair', f'{x}.nii.gz'), val_imgs))#, os.path.join(args.image_path, 't1_75', f'{x}.nii')], train_imgs))
    val_lab_paths = list(map(lambda x: os.path.join(args.image_path, 'labels', f'{x}.nii.gz'), val_imgs))
    logging.info(f"Found a total of {len(val_img_paths)} validation images")
    

    logging.info("Instantiating Data Augmentation Transforms")
    augmentation_params =  [A.Rotate(p=.8, limit=15, interpolation=cv2.INTER_CUBIC,
                                border_mode=cv2.BORDER_CONSTANT, value=(-4, -4),  mask_value=0)]
    augmentation = DataAugmentation(augmentation_params)

    aconfig = {
        "Rotation": {"p": .8, "limit": 15, "interpolation": "cubic", "border_mode": "constant"},
        }

    print("Augmentation Transforms and Parameters")
    for k, v in aconfig.items():
        print(f"\t {k}")
        for kk, vv in v.items():
            print(f"\t\t -{kk}: {vv}")


    train_feeder = ImageFeeder(flr_paths=train_img_paths,
                               tar_paths=train_lab_paths,
                               t1w_paths=None,
                               batch_size=args.batch,
                               preprocessing=None,
                               augmentation=augmentation,
                               shuffle=True)

    val_feeder = ImageFeeder(flr_paths=val_img_paths,
                              tar_paths=val_lab_paths,
                              t1w_paths=None,
                              preprocessing=None,
                              shuffle=False,
                              batch_size=1)

    outpath = os.path.join(args.output, datetime.today().strftime("%Y_%m_%d_%H_%M_%S"))
    print("Model Instantiation")

    callbacks = [
                ReduceLROnPlateau(monitor='val_loss', patience=10, factor=0.1),
                EarlyStopping( monitor='val_loss', patience=15),#]
                ModelCheckpoint(os.path.join(outpath, 'ckp'), monitor="val_dice_coeff", save_best_only=True, save_weights_only=True)]
    
    model = get_base_model((256, 256, 1), args.wpath)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.lr, clipnorm=1e-5),
        loss=tversky_loss,
        metrics=[dice_coeff])

    print("Model Summary")
    print(model.summary())

    print("Start Training")

    history = model.fit(
                    train_feeder,
                    epochs=args.epochs,
                    callbacks=callbacks,
                    validation_data=val_feeder)

    print("Saving the results")
    # now save the weights into the proper directory
    df = pd.DataFrame.from_dict(history.history)
    df.to_csv(os.path.join(outpath, 'history.csv'), sep=',', index=None)

    model.save_weights(filepath=os.path.join(outpath, 'weights.h5'))
    

if __name__ == "__main__":
    main()