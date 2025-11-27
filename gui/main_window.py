import os
import FreeSimpleGUI as sg
from gui.panels.loading_panel import LoadingPanel
from gui.panels.preview_panel import ImagePreviewPanel

from sci_segmentator.core.loader import _read_dicom_study
from gui.utilities import _format_image_metadata, _series_display_names_from_metadata_lut
__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]



class MainWindow:

    def __init__(self, config: dict, string: dict):
        '''
        Initializer for the GUI.
        
        :param self: Description
        :param config: Description
        :type config: dict
        :param string: Description
        :type string: dict
        '''

        self.config = config
        self.string = string

        self.loading_panel = LoadingPanel(config, string["Loader"])
        self.preview_panel = ImagePreviewPanel(config, string["ImagePreview"])
        _ = self._build_layout()


    def _set_them(self):
        ...

    def _build_layout(self):

        self._layout = [[
                        sg.Column(self.loading_panel.layout),
                        sg.VSeparator(),
                        sg.Column(self.preview_panel.layout)]]


    def run(self):

        # Create the window
        window = sg.Window(self.string["MainTitle"], self._layout, resizable=True)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()
            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break


            if event == "-FOLDER-":
                folder = values["-FOLDER-"]

                if os.path.isdir(folder):
                    print(folder)
                    # --- aggiorna serie ---
                    images, metadatas = _read_dicom_study(folder)

                    series_lut = [_series_display_names_from_metadata_lut(metadata) for metadata in metadatas]
                    series_names = [list(e.keys())[0] for e in series_lut]
                    window["-SERIES_LIST-"].update(values=series_names)
                    window["-DROPDOWN_FLAIR-"].update(values=series_names)
                    window["-DROPDOWN_T1W-"].update(values=series_names)

                # --- aggiorna dati paziente ---
                window["-PATIENT_NAME-"].update(metadatas[0]["0010|0010"])
                window["-PATIENT_AGE-"].update("N/A") #Change
                window["-PATIENT_SEX-"].update(metadatas[0]["0010|0040"])

        # Finish up by removing from the screen
        window.close()