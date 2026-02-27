from checkers.engine.inference_interface import InferenceInterface
from checkers.data.data_interface import DataInterface
from checkers.engine.classic.classic import Classic
from checkers.data.history_inference import HistoryInference
class InferenceFactory:
    """
    """

    @staticmethod
    def create_inference(key:str, data:DataInterface)->InferenceInterface:                
        match key:
            case "classic":
                return Classic()
            #case "SL":
            #    return SupervisedLearning()
            #case "RL":
            #    return ReinforcementLearning()
            case "view":
                return HistoryInference(data)
            case _:
                # need in "player"
                return None
