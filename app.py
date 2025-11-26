from gui.locale.loader import load_language
from gui.main_window import MainWindow


__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


def main():

    # here read the configuration and the chosen language
    string = load_language("en")

    window = MainWindow(config={}, string=string)

    window.run()

if __name__ == "__main__":
    main()