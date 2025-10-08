import os
import itk
import logging
from typing import List

__author__ = ["Riccardo Biondi", "Nicolas Biondini"]
__email__ = ["riccardo.biondi7@unibo.it", "nicolas.biondini2@unibo.it"]


logger = logging.getLogger(__file__)


def get_multimap_parameters(
                        metric: str = "AdvancedMattesMutualInformation",
                        resolutions: int = 4,
                        modalities: List[str] = ["rigid", "affine"],
                        transform_combination: str = "Compose",
                        initial_tranform: bool = False):
    
    logger.debug(f"Get Multimap Registration Parameters: - combined transforms: {modalities}  - similarity metric: {metric} - transform combination technique: {transform_combination} - number of resolution: {resolutions} - has initial tranform: {initial_tranform}")
    parameter_object = itk.ParameterObject.New()

    for modality in modalities:
        parameter_map = parameter_object.GetDefaultParameterMap(modality, resolutions)
        parameter_map["Metric"] = [metric]
        parameter_map["Interpolator"] = ["BSplineInterpolatorFloat"]
        parameter_map["HowToCombineTransforms"] = [transform_combination]

        if initial_tranform:
            parameter_map["InitialTransformParametersFilename"] = ["NoInitialTransform"]

        parameter_object.AddParameterMap(parameter_map)

    return parameter_object