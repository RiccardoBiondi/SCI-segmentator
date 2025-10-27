"""
Generic utilities file
"""
import os
import tensorflow as tf



def _get_gpu_report() -> str:
    
    gpus =  tf.config.list_physical_devices("GPU")

    ngpus = len(gpus)

    return f"Found {ngpus} Visible GPUs"
