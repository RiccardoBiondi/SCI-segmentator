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
            [
                sg.Input(key="-FOLDER-", enable_events=True),
                sg.FolderBrowse(self.string["Browse"])
            ]
        ]

        # --- Dati paziente (ora sopra le serie) ---
        patient_info = [
            [sg.Text(self.string["PatientName"]), sg.Text("", key="-PATIENT_NAME-", size=(40,1))],
            [sg.Text(self.string["PatientAge"]), sg.Text("", key="-PATIENT_AGE-", size=(40,1))],
            [sg.Text(self.string["PatientSex"]), sg.Text("", key="-PATIENT_SEX-", size=(40,1))],
            [sg.Text(self.string["StudyDate"]), sg.Text("", key="-STUDY_DATE-", size=(40,1))]

        ]

        # --- Lista delle serie ---
        series_list = [
            [
                sg.Listbox(
                    values=[],
                    key="-SERIES_LIST-",
                    size=(40, 15),
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                )
            ]
        ]

        dropdown_menu = [
            [sg.Text("FLAIR:"), sg.Combo(values=[], key="-DROPDOWN_FLAIR-", readonly=True, size=(40, 1), enable_events=True)],
            [sg.Text("T1W:  "), sg.Combo(values=[], key="-DROPDOWN_T1W-", readonly=True, size=(40, 1), enable_events=True)]
        ]



        layout = [
            [sg.Frame(self.string["DICOMFolder"], folder_selector)],
            [
                sg.Column([
                    [sg.Frame(self.string["PatientData"], patient_info)],
                    [sg.Frame(self.string["DICOMSeries"], series_list)],
                    [sg.Frame(self.string["ImageSelector"], dropdown_menu )]
                ])
            ],
            [sg.Button(self.string["Segment"],  disabled=True, key="-SEGMENT-"), sg.Button(self.string["PostProcess"],  key="-POSTPROCESS-", disabled=True)]
        ]

        return layout
    




'''
 while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Esci"):
            break

        # Quando l'utente seleziona una cartella
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]

            if os.path.isdir(folder):

                # --- aggiorna serie ---
                lista_serie = leggi_serie(folder)
                window["-SERIES_LIST-"].update(lista_serie)

                # --- aggiorna dati paziente ---
                nome, eta, sesso = leggi_dati_paziente(folder)
                window["-PATIENT_NAME-"].update(nome)
                window["-PATIENT_AGE-"].update(eta)
                window["-PATIENT_SEX-"].update(sesso)

    window.close()'''