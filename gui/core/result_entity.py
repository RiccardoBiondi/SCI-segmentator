import os
import itk
from typing import NoReturn


class ResultEntity:

    def __init__(self):
        
        self._status = False

    @property
    def status(self) -> bool:
        return self._status
    
    def reset() -> NoReturn:
        ...