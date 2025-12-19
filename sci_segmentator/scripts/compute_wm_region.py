import os
import itk
import logging
import argparse
import numpy as np
from sklearn.mixture import GaussianMixture

from sci_segmentator.core.filters import itk_binary_threshold
from sci_segmentator.core.filters import itk_binary_fill_hole

__author__ = ["Nicolas Biondini", "Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


def parse_args():
    ...


def run(t1: itk.Image, intialization: itk.Image) -> itk.Image:
    
    logging.debug(f"Finding pobability weights for GMM initialization")
    image = itk.GetArrayFromImage(t1)
    mask = itk.GetArrayFromImage(intialization)
    brain_vx = np.sum((mask > 0).astype(np.uint8))
    wm_vx = np.sum((mask == 1).astype(np.uint8))
    gm_vx = np.sum((mask == 2).astype(np.uint8))
    csf_vx = np.sum((mask ==3).astype(np.uint8))
    
    proba_weights = [wm_vx / brain_vx, gm_vx / brain_vx, csf_vx / brain_vx]

    logging.debug("Computing Initiali Means for GMM model")
    means = np.asarray([np.mean(image[mask == 1]), np.mean(image[mask == 2]), np.mean(image[mask == 3])])
    
    logging.debug("Computing the Brain Regions")

    model = GaussianMixture(
                n_components = 3,
                covariance_type = 'full',
                tol = 0.001,
                max_iter = 10000,
                init_params = 'k-means++',
                means_init = means.reshape((3, 1)),
                weights_init = proba_weights)
    #updating the funtion to find the labels
    model.fit( np.reshape( image[mask > 0], (-1,1) ) )
    labeled = model.predict( np.reshape( image[mask > 0], (-1,1) ))

    output = np.zeros(image.shape, dtype=np.uint8)
    output[mask > 0] = labeled.astype(np.uint8)

    output = itk.GetImageFromArray(output)
    _ = output.SetSpacing(t1.GetSpacing())
    _ = output.SetOrigin(t1.GetOrigin())
    _ = output.SetDirection(t1.GetDirection())

    output = itk_binary_threshold(output, lower_thr=2, upper_thr=2)
    output = itk_binary_fill_hole(output.GetOutput())

    return output

def main():
    ...

if __name__ == "__main__":
    main()