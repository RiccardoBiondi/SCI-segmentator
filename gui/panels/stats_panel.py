import FreeSimpleGUI as sg

__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


class SegmentationStatsPanel:
    """
    """

    def __init__(self, config, string):
        """
        """
        self.config = config
        self.string = string
        self._layout = self._build_layout()

    @property
    def layout(self):
        return self._layout
    
    def _build_layout(self):
        '''
        '''
        layout = [
            [sg.Frame(self.string["Title"],[ [sg.Text("placeholder"), sg.Text("", key="-PLACE_HOLDER-", size=(40,1))]])],
        ]
        return layout