import os
import logging
from typing import List, Dict
__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]

# Patient Name (‘0010’, ‘0010’)
# Patient ID (‘0010’, ‘0020’)
# Patient Sex (‘0010’, ‘0040’)
# metadata["0020|0011"] 

PATIENT_METADATA : List[str] = ["0010|0010", "0010|0020", "0010|0040", "0020|0011"]

def _format_image_metadata(metadata, replacement: str = "N/A", keys: List[str] = PATIENT_METADATA) -> Dict[str, str]:
    print(metadata)
    out_dict = {}
    for k in keys:
        print(k)
        
        value = metadata[k] if metadata.HasKey(k) else replacement
        out_dict.update({k:value})
    return out_dict


def _series_display_names_from_metadata_lut(metadata: Dict[str, str]) -> Dict[str, str]:

    meta_keys = list(metadata.keys())
    
    modality = metadata["0008|0060"] if "0008|0060" in meta_keys else " "
    description =  metadata["0008|103e"] if "0008|103e" in meta_keys else " "
    number = metadata["0020|0011"] if "0020|0011" in meta_keys else " "
    series_uid = metadata["0020|000e"]
    print(series_uid)
    return {"-".join([number, description, modality]): series_uid}
