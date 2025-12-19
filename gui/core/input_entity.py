import os
import itk
import logging
from sci_segmentator.core.loader import _read_dicom_study
from sci_segmentator.core.filters import  itk_orient_image_to_axial
from sci_segmentator.core.filters import  itk_cast

from gui.utilities import _format_image_metadata, _series_display_names_from_metadata
from functools import cache
from typing import NoReturn, List, Dict

__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


DEFAULT_PATIENT_DATA_DICT = {
       "-PATIENT_NAME-": "",
       "-PATIENT_AGE-": "",
       "-PATIENT_SEX-": "",
       "-STUDY_DATE-": ""}

class InputEntity:
    """
    """

    def __init__(self):
        """
        """
        self.reset()

    def __getitem__(self, id_str: str):
        """
        """

        if id_str in self._series_names:
            return self._image_lut[self._series_lut[id_str]]
        else:
            return None

    @property
    def status(self) -> bool:
        """
        """
        return self._status
    
    @property
    def series_names(self) -> List[str]:
        '''
        ''' 
        return self._series_names
     
    @property
    def patient_data(self) -> Dict[str, str]:
        """
        Docstring for patient_data
        
        :param self: Description
        :return: Description
        :rtype: Dict[str, str]
        """
        return self._patient_data
    
    def reset(self) -> NoReturn:
        """
        """
        self._status = False
        self._series_lut = {}
        self._patient_data = { "-PATIENT_NAME-": "", "-PATIENT_AGE-": "", "-PATIENT_SEX-": "", "-STUDY_DATE-": ""}
        self._series_names = []

    def update(self, folder):
        """
        Read the foldeer and initialize 
        """

        # read DICOM

        try:
            images, metadatas = _read_dicom_study(folder)
            
            self._image_lut = {metadata["0020|000e"] :  itk_cast(itk_orient_image_to_axial(image).GetOutput(), itk.F).GetOutput() for image, metadata in zip(images, metadatas)}
            self._series_lut = {_series_display_names_from_metadata(metadata) : metadata["0020|000e"] for metadata in metadatas}

            self._series_names = sorted(list(self._series_lut.keys()))

            # now create the patient data dict
            
            self.patient_data["-PATIENT_NAME-"] = metadatas[0]["0010|0010"]
            self.patient_data["-PATIENT_AGE-"] = "N/A"
            self.patient_data["-PATIENT_SEX-"] = metadatas[0]["0010|0040"]
            self.patient_data["-STUDY_DATE-"] = metadatas[0]["0008|0020"]


            self._status = True
        except Exception as e:
            logging.error(e)
            self.reset()            
