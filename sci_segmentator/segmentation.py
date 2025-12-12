import os
import itk
import logging
import numpy as np
from typing import List

import onnxruntime as ort
import FreeSimpleGUI as sg

EP_list = ['CUDAExecutionProvider', 'CPUExecutionProvider']

def run(flair: itk.Image, model_list: List[str], logger=logging) -> itk.Image:
    
    logger.debug("Converting input flair image to tensor")
    tensor = itk.GetArrayFromImage(flair)[..., np.newaxis]
    logger.debug(f"Input tensor shape: {tensor.shape}")
    # for each model in list, segment and add the segmentation to the results
    results = []
    for i, model in enumerate(model_list):
        logger.debug(f"Segmenting with {i + 1}-th model: {model}")
        sg.one_line_progress_meter("Perform Sagmentation", i+1, len(model_list))
        sess = ort.InferenceSession( model, providers=EP_list)
        res = sess.run([sess.get_outputs()[0].name], {sess.get_inputs()[0].name: tensor})[0]
        results.append(res)

    results = np.asarray(results)
    logger.debug(f"Segmentation DONE, results shape is: {results.shape} -> Combininig activation maps by average")

    results = results.mean(axis=(0, -1))
    logger.debug(f"DONE: Resulting prediction shape: {results.shape}")
    logger.debug("Converting Array to ITK Image")
    results = itk.GetImageFromArray(results)
    _ = results.SetSpacing(flair.GetSpacing()) 
    _ = results.SetOrigin(flair.GetOrigin()) 
    _ = results.SetDirection(flair.GetDirection())


    return results


def main():
    ...


if __name__ == "__main__":
    main()