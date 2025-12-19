
import FreeSimpleGUI as sg
import numpy as np
from gui.utilities import to_png_bytes
from PIL import Image

__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


class ImagePreviewPanel:
    """

    """

    def __init__(self, config, string):

        self.config = config
        self.string =string
        self._layout = self._build_layout()
        self._slider_range = 0

    @property
    def layout(self):
        return self._layout
    
    @property
    def slider_range(self) -> int:
        return self._slider_range
    
    @slider_range.setter
    def slider_range(self, value: int):
        self._slider_range = value
        self._slider.update(range=(0, value))

    
    def _build_layout(self):
        """
        """

        self._slider = sg.Slider(range=(0, 0), orientation="h", key="-SLIDER-", enable_events=True, expand_x=True)
        preview_panel = [
                [sg.Image(key="-PREVIEW-", size=(512, 512), expand_x=True, expand_y=True)],
                [self._slider]
                ]

        layout = [
            [sg.Frame(self.string["Title"], preview_panel)],
        ]

        return layout
    

    def update_preview(self, window, image, idx):
        '''
        '''

        frame = to_png_bytes(image[idx], size=(512, 512))
        window["-SLIDER-"].update(value=int(idx))
        window["-PREVIEW-"].update(data=frame)

