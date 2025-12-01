import os
import itk
import numpy as np
import FreeSimpleGUI as sg
from gui.panels.loading_panel import LoadingPanel
from gui.panels.preview_panel import ImagePreviewPanel

from sci_segmentator.core.loader import _read_dicom_study
from gui.utilities import _format_image_metadata, _series_display_names_from_metadata

from sci_segmentator import preprocess 

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

        # TODO Bind the logic in some internal class functions, in order to clean up the code

        # Create the window
        window = sg.Window(self.string["MainTitle"], self._layout, resizable=True)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()

            print(values)
            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break


            if event == "-FOLDER-":
                folder = values["-FOLDER-"]

                if os.path.isdir(folder):
                    # --- aggiorna serie ---
                    images, metadatas = _read_dicom_study(folder)
                    image_lut = {metadata["0020|000e"] : [image, metadata] for image, metadata in zip(images, metadatas)}

                    series_lut = {_series_display_names_from_metadata(metadata) : metadata["0020|000e"] for metadata in metadatas}

                    print(series_lut)                    
                    series_names = sorted(list(series_lut.keys()))

                    window["-SERIES_LIST-"].update(values=series_names)
                    window["-DROPDOWN_FLAIR-"].update(values=series_names)
                    window["-DROPDOWN_T1W-"].update(values=series_names)

                    window["-PATIENT_NAME-"].update(metadatas[0]["0010|0010"])
                    window["-PATIENT_AGE-"].update("N/A") #Change
                    window["-PATIENT_SEX-"].update(metadatas[0]["0010|0040"])
                    window["-STUDY_DATE-"].update(metadatas[0]["0008|0020"])

            if event == "-SERIES_LIST-":

                selected_uid = series_lut[values["-SERIES_LIST-"][0]]
                to_display = itk.GetArrayFromImage(image_lut[selected_uid][0])
                to_display = 255 * (to_display - to_display.min()) / (to_display.max() - to_display.min())
                self.preview_panel.slider_range = to_display.shape[0] - 1
                self.preview_panel.update_preview(window, to_display.astype(np.uint8), idx=to_display.shape[0] // 2)

            if event == "-SLIDER-":

                self.preview_panel.update_preview(window, to_display, idx=int(values["-SLIDER-"]))

                # --- aggiorna dati paziente ---
            if event ==  self.string["Loader"]["Segment"]:
                
                # this action will start the segmentation.
                # First of all, it will check that a name for the flair and t1 is provided,
                # It will also check if the ids are different, since T1 and FLAIR are stored in different series
                if (values["-DROPDOWN_FLAIR-"] != '') & (values["-DROPDOWN_T1W-"] != '') & (values["-DROPDOWN_T1W-"] != values["-DROPDOWN_FLAIR-"]): 

                    # chiamo la funzione per fare il preprocessing
                    out = preprocess.run(flair=image_lut[series_lut[values["-DROPDOWN_FLAIR-"]]][0], t1=image_lut[series_lut[values["-DROPDOWN_T1W-"]]][0])
                    print(out)
        # Finish up by removing from the screen
        window.close()