import FreeSimpleGUI as sg
from gui.panels.loading_panel import LoadingPanel

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

        _ = self._build_layout()


    def _set_them(self):
        ...

    def _build_layout(self):


        self.loading_layout = self.loading_panel.layout

    def run(self):

        #layout = [[sg.Text("What's your name?")],
        #  [sg.Input(key='-INPUT-')],
        #  [sg.Text(size=(40,1), key='-OUTPUT-')],
        #  [sg.Button('Ok'), sg.Button('Quit')]]

        # Create the window
        window = sg.Window(self.string["MainTitle"], self.loading_layout)

        # Display and interact with the Window using an Event Loop
        while True:
            event, values = window.read()
            # See if user wants to quit or window was closed
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break
            # Output a message to the window
            window['-OUTPUT-'].update('Hello ' + values['-INPUT-'] + "! Thanks for trying FreeSimpleGUI")

        # Finish up by removing from the screen
        window.close()