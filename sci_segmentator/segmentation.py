import os
import itk
import logging
import numpy as np
from typing import List

import onnxruntime as ort
import FreeSimpleGUI as sg

EP_list = ['CUDAExecutionProvider', 'CPUExecutionProvider']

so = ort.SessionOptions()
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
so.enable_mem_pattern = True
so.enable_cpu_mem_arena = False
so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
so.intra_op_num_threads = 1


def run(flair: itk.Image, model_list: List[str], logger=logging) -> itk.Image:

    # configuring ONNX inference to avoid memory leack
    
    logger.debug("Converting input flair image to tensor")
    tensor = itk.GetArrayFromImage(flair)[..., np.newaxis]
    logger.debug(f"Input tensor shape: {tensor.shape}")
    # for each model in list, segment and add the segmentation to the results
    results = []
    sg.one_line_progress_meter("Perform Sagmentation", 0, len(model_list))
    for i, model in enumerate(model_list):
        logger.debug(f"Segmenting with {i + 1}-th model: {model}")
        sess = ort.InferenceSession( model, so, providers=EP_list)
        res = np.concatenate([sess.run([sess.get_outputs()[0].name], {sess.get_inputs()[0].name: tn[np.newaxis]})[0] for tn in tensor])
        logging.debug(f"{i+1}-th prediction tensor shape: {res.shape}")
        results.append(res)

        sg.one_line_progress_meter("Perform Sagmentation", i + 1, len(model_list))

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