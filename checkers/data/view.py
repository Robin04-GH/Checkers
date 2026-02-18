from typing import Optional
from checkers.engine.inference_interface import InferenceInterface
from checkers.data.db_manager import DatabaseManager
from checkers.data.pdn_manager import PdnManager
from checkers.data.view_interface import ViewInterface
from checkers.engine.game.move import Move

class View(InferenceInterface):
    """
    """
    def __init__(self, import_pdn_name:str, db:DatabaseManager, pdn:PdnManager):
        super().__init__()
        self.view : ViewInterface = pdn if import_pdn_name != None and len(import_pdn_name) > 0 else db

    def run(self, moves:set[Move])->Optional[Move]:
        pass

