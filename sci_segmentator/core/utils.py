"""
Generic utilities file
"""
import os
import numpy as np
import tensorflow as tf



def _get_gpu_report() -> str:
    
    gpus =  tf.config.list_physical_devices("GPU")

    ngpus = len(gpus)

    return f"Found {ngpus} Visible GPUs"

def _set_accelerator(accelerator: str):
    
    gpus =  tf.config.list_physical_devices("GPU")

    if (len(gpus) == 0) | (accelerator == "cpu"):
        print(f"Running on CPU")
        tf.config.set_visible_devices([], 'GPU')
    else:
        print(f"Found {len(gpus)} gpus. Running on GPU")


def _set_random_seed(seed: int):
    
    _ = tf.keras.utils.set_random_seed(seed)
    _ = np.random.seed(seed)