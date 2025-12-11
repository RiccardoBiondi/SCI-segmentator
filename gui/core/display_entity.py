import os
import itk
import numpy as np
from typing import NoReturn


class DisplayITKImageEntity:

    BLACK_IMAGE = np.zeros((256, 256))

    def __init__(self):

        self.reset()

    @property
    def status(self) -> bool:
        return self._status
    
    def reset(self) -> NoReturn:
        
        self._status = False
        self._image = self.BLACK_IMAGE # substitute with a default value!
        self._slider_range = 0

    @property
    def image(self) -> np.ndarray:
        return self._image
    
    @property
    def slider_range(self):
        return self._slider_range

    def update(self, itk_image: itk.Image):
        
        try:
            self._image = itk.GetArrayFromImage(itk_image)
            self._image =  255 * (self._image - self._image.min()) / (self._image.max() - self._image.min())

            # TODO: implement also to consider the 2D case
            if len(self._image.shape) == 3:
                self._slider_range = self._image.shape[0]
        except:
            self.reset()