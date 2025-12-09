import os
import itk
from typing import NoReturn
from sci_segmentator import preprocess 

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
    
    def output(self):
        return self._output

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
        print("Ciaooooo")

        self._output = preprocess.run(flair=flair, t1=t1)

        print(self._output)

        self._status = True
        
        