import os 
from gui.locale.loader import load_language
from gui.main_window import MainWindow
import logging
import FreeSimpleGUI as sg

__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


def main():

    # here read the configuration and the chosen language

    basedir = os.path.dirname(__file__)

    log_level = logging.DEBUG#[min(args.verbosity, max(log_levels.keys()))]
    log_format = '%(asctime)s - %(name)s -  %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)
    string = load_language("it", os.path.join(basedir, "gui", "locale"))


    window = MainWindow(config={"basedir": basedir}, string=string)
    window.run()

if __name__ == "__main__":
    main()