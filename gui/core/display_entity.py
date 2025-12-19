import os
import itk
import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import NoReturn
from gui.utilities import to_png_bytes
from PIL import Image
import io

def create_overlay(image, overlay, alpha=200):
    """
    """
    overlay.putalpha(alpha)
    # Calcolo posizione
    x = (image.width - overlay.width) // 2
    y = (image.height - overlay.height) // 2

    # Composizione
    result = image.copy()
    result.paste(overlay, (x, y), mask=overlay)

    return result

class DisplayITKImageEntity:

    BLACK_IMAGE = np.zeros((256, 256))

    def __init__(self):

        self.reset()

    @property
    def status(self) -> bool:
        return self._status

    @property
    def image(self) -> np.ndarray:
        return self._image
    
    @property
    def slider_range(self):
        return self._slider_range

    
    def reset(self) -> NoReturn:
        
        self._status = False
        self._image = self.BLACK_IMAGE # substitute with a default value!
        self._slider_range = 0


    def update(self, itk_image: itk.Image):
        
        try:

            self._image = itk.GetArrayFromImage(itk_image)
            self._image =  255 * (self._image - self._image.min()) / (self._image.max() - self._image.min())
            self._image = self._image.astype(np.uint8)
            if len(self._image.shape) == 3:
                self._slider_range = self._image.shape[0]
            # TODO: implement also to consider the 2D case
        except Exception as e:
            logging.error(e)
            self.reset()