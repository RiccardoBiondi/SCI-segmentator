import os
import itk
import logging
from typing import NoReturn
from sci_segmentator import preprocess 
from sci_segmentator import segmentation
from sci_segmentator.scripts import resample_onto_reference

class SegmentatorEntity:
    """
    """

    def __init__(self):
        """
        """
        self.reset()

    @property
    def status(self) -> bool:
        """
        """
        return self._status
  
    @property
    def is_executable(self) -> bool:
        '''
        '''
        return self._is_executable
    
    @is_executable.setter
    def is_executable(self, value: bool) -> NoReturn:
        self._is_executable = value
    
    @property
    def output(self):
        return self._output
    
    @property
    def flair(self):
        return self._flair
    
    @property
    def t1(self):
        return self._t1

    def reset(self) -> NoReturn:
        """
        """
        self._status = False
        self._is_executable = False

        self._t1 = None
        self._flair = None
        self._output = None

    def update(self, t1, flair) -> NoReturn:
        """
        """        

        try:
            self._t1 = t1
            self._flair = flair
            seg_input = preprocess.run(flair=flair, t1=t1)
            #itk.imwrite(seg_input.GetOutput(), "/DATA/flair_test.nii.gz")
            self._output = segmentation.run(seg_input.GetOutput(), model_list=["./fixtures/ensamble_0.onnx"])#, "./fixtures/ensamble_1.onnx"])#, "./fixtures/ensamble_2.onnx", "./fixtures/ensamble_3.onnx", "./fixtures/ensamble_4.onnx"])
            ## resampling output imgae onto reference flair
            #itk.imwrite(self._output, "/DATA/seg_test.nii.gz")
            self._output = resample_onto_reference.run(self._output, flair, clamp=True, interpolator="bspline").GetOutput()
            self._status = True
        except Exception as e:
            logging.error(e)
        
        