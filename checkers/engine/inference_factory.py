from checkers.engine.inference_interface import InferenceInterface
from checkers.config_manager import ConfigManager
from checkers.data.db_manager import DatabaseManager
from checkers.data.pdn_manager import PdnManager
from checkers.engine.classic.classic import Classic
from checkers.data.view import View
class InferenceFactory:
    """
    """

    @staticmethod
    def create_inference(config:ConfigManager, engine:str, db:DatabaseManager, pdn:PdnManager)->InferenceInterface:                
        if config.execution_mode == "play":
            match engine:
                case "classic":
                    return Classic()
                #case "SL":
                #    return SupervisedLearning()
                #case "RL":
                #    return ReinforcementLearning()
                case _:
                    # need in "player"
                    return None
        elif config.execution_mode == "view":
            return View(config.import_pdn_name, db, pdn)
        else:
            return None

