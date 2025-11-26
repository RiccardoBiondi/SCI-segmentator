from typing import Dict
import FreeSimpleGUI as sg


class LoadingPanel:

    def __init__(self, config, string):

        self.config = config
        self.string =string
        self._layout = self._build_layout()

    
    @property
    def layout(self):
        
        return self._layout

    def _build_layout(self):
        # --- Selettore cartella ---
        folder_selector = [
            [sg.Text(self.string["SelectDICOMFolder"])],
            [
                sg.Input(key="-FOLDER-", enable_events=True),
                sg.FolderBrowse(self.string["Browse"])
            ]
        ]

        # --- Dati paziente (ora sopra le serie) ---
        patient_info = [
            [sg.Text(self.string["PatientName"]), sg.Text("", key="-PATIENT_NAME-", size=(30,1))],
            [sg.Text(self.string["PatientAge"]), sg.Text("", key="-PATIENT_AGE-", size=(30,1))],
            [sg.Text(self.string["PatientSex"]), sg.Text("", key="-PATIENT_SEX-", size=(30,1))]
        ]

        # --- Lista delle serie ---
        series_list = [
            [
                sg.Listbox(
                    values=[],
                    key="-SERIES_LIST-",
                    size=(40, 15),
                    enable_events=True
                )
            ]
        ]

        layout = [
            [sg.Frame(self.string["DICOMFolder"], folder_selector)],
            [
                sg.Column([
                    [sg.Frame(self.string["PatientData"], patient_info)],
                    [sg.Frame(self.string["DICOMSeries"], series_list)]
                ])
            ],
            [sg.Button("Esci")]
        ]

        return layout