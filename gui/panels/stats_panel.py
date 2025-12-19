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

        general_stats = [
            [sg.Text(self.string["LesionBurden"], size=(20, 1)), sg.Text("", key="-LESION_BURDEN-", size=(40,1))],
            [sg.Text(self.string["NumberOfLesions"], size=(20, 1)), sg.Text("", key="-NUMBER_OF_LESIONS-", size=(40,1))],
        ]

        involvment_stats = [
            [sg.Text(self.string["Brain"], size=(20, 1)), sg.Text("", key="-BRAIN_INVOLVMENT-", size=(40,1))],
            [sg.Text(self.string["WhiteMatter"], size=(20, 1)), sg.Text("", key="-WM_INVOLVMENT-", size=(40,1))],
            [sg.Text(self.string["ACA"], size=(20, 1)), sg.Text("", key="-ACA_INVOLVMENT-", size=(40,1))],
            [sg.Text(self.string["MCA"], size=(20, 1)), sg.Text("", key="-MCA_INVOLVMENT-", size=(40,1))],
            [sg.Text(self.string["PCA"], size=(20, 1)), sg.Text("", key="-PCA_INVOLVMENT-", size=(40,1))]
        ]

        numerosity_stats = [
            [sg.Text(self.string["ACA"], size=(20, 1)), sg.Text("", key="-ACA_NUMBER-", size=(40,1))],
            [sg.Text(self.string["MCA"], size=(20, 1)), sg.Text("", key="-MCA_NUMBER-", size=(40,1))],
            [sg.Text(self.string["PCA"], size=(20, 1)), sg.Text("", key="-PCA_NUMBER-", size=(40,1))]

        ]
        layout = [
           [
                sg.Column([
                    [sg.Frame(self.string["GeneralTitle"], general_stats)],
                    [sg.Frame(self.string["InvolvmentTitle"], involvment_stats)],
                    [sg.Frame(self.string["NumberTitle"], numerosity_stats)]
                ])
            ],
        ]
        return layout