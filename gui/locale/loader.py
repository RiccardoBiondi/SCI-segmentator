import os
import yaml
import logging
from typing import Dict

__author__ = ["Riccardo Biondi"]
__email__ = ["riccardo.biondi7@unibo.it"]


def load_language(language: str = "it", here: str = "."):# -> Dict[str]:
    '''
    '''

    with open(os.path.join(here, f"{language}.yaml")) as stream:
        try:
            string = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)

    #string = yaml.safe_load()
    
    return string