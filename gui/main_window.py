import os
import itk
import numpy as np
import FreeSimpleGUI as sg
from gui.panels.loading_panel import LoadingPanel
from gui.panels.preview_panel import ImagePreviewPanel
from gui.panels.stats_panel   import SegmentationStatsPanel
from gui.core.input_entity import InputEntity
from gui.core.display_entity import DisplayITKImageEntity
from gui.core.segmentation_entity import SegmentatorEntity



from sci_segmentator.core.loader import _read_dicom_study
from gui.utilities import _format_image_metadata, _series_display_names_from_metadata



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
        self.stats_panel = SegmentationStatsPanel(config, string["Stats"])
        _ = self._build_layout()


    def _set_theme(self):
        ...

    def _build_layout(self):

        self._layout = [[
                        sg.Column(self.loading_panel.layout),
                        sg.VSeparator(),
                        sg.Column(self.preview_panel.layout),
                        sg.VSeparator(),
                        sg.Column(self.stats_panel.layout)]]


    def run(self):

        # TODO Bind the logic in some internal class functions, in order to clean up the code

        # Create the window
        window = sg.Window(self.string["MainTitle"], self._layout, resizable=True)


        # now create the instance of the main GUI entities

        input_entity = InputEntity()
        display_entity = DisplayITKImageEntity()
        segmentation_entity = SegmentatorEntity()

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()

                        # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break

            if event == "-FOLDER-":

                #  first of all, if a current status is present, reset all.
                if input_entity.status:
                    _ = input_entity.reset()
                    _ = display_entity.reset()
                    _ = segmentation_entity.reset()


                folder = values["-FOLDER-"]

                if os.path.isdir(folder): # TODO Incorporate this condition inside the input entity
                    # --- aggiorna serie ---
                    input_entity.update(folder)
                    
                    #Here update all the required fields
                    window["-SERIES_LIST-"].update(values=input_entity.series_names)
                    window["-DROPDOWN_FLAIR-"].update(values=input_entity.series_names)
                    window["-DROPDOWN_T1W-"].update(values=input_entity.series_names)

                    window["-PATIENT_NAME-"].update(input_entity.patient_data["-PATIENT_NAME-"])
                    window["-PATIENT_AGE-"].update(input_entity.patient_data["-PATIENT_AGE-"]) #Change
                    window["-PATIENT_SEX-"].update(input_entity.patient_data["-PATIENT_SEX-"])
                    window["-STUDY_DATE-"].update(input_entity.patient_data["-STUDY_DATE-"])

            if event == "-SERIES_LIST-":
                # now prepare the entity to use to display the image
                series_uid = values["-SERIES_LIST-"][0] if len(values["-SERIES_LIST-"]) != 0 else None
                display_entity.update(input_entity[series_uid])
                self.preview_panel.slider_range = display_entity.slider_range
                self.preview_panel.update_preview(window, display_entity.image, idx=display_entity.slider_range // 2)

            if event == "-SLIDER-":
                self.preview_panel.update_preview(window, display_entity.image, idx=int(values["-SLIDER-"]))

                # --- aggiorna dati paziente ---
            if event in ["-DROPDOWN_FLAIR-", "-DROPDOWN_T1W-"]:
                segmentation_entity.is_executable =  ((values["-DROPDOWN_FLAIR-"] != "") &( values["-DROPDOWN_T1W-"] != "")) & ((values["-DROPDOWN_T1W-"] != values["-DROPDOWN_FLAIR-"]))
                window["-SEGMENT-"].update(disabled=not segmentation_entity.is_executable)

            if event ==  "-SEGMENT-":
                    # if a current segmentation exists, then reset the objecgt
                    if segmentation_entity.status:
                        segmentation_entity.reset()
                    segmentation_entity.update(t1=input_entity[values["-DROPDOWN_T1W-"]]2, flair=input_entity[values["-DROPDOWN_FLAIR-"]])
                    window["-POSTPROCESS-"].update(disabled= not segmentation_entity.status)
                 
                
                # this action will start the segmentation.
                # First of all, it will check that a name for the flair and t1 is provided,
                # It will also check if the ids are different, since T1 and FLAIR are stored in different series

                    # chiamo la funzione per fare il preprocessing
#                    out = preprocess.run(flair=image_lut[series_lut[values["-DROPDOWN_FLAIR-"]]][0], t1=image_lut[series_lut[values["-DROPDOWN_T1W-"]]][0])
#                    print(out)
        # Finish up by removing from the screen
#        window.close()