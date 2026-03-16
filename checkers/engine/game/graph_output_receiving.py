from typing import Optional
from checkers.engine.game.state import State
from checkers.engine.game.move_sequence import EnumEngineMoving, MoveSequence
from checkers.engine.game.move import Move

class GraphOutputReceiving:
    """
    """

    def __init__(self, state:State, move_sequence:MoveSequence):
        self.state = state
        self.move_sequence = move_sequence

    def print_string(self, string:str)->int:
        # print(f"Msg=" + string)
        match string:
            case "QUIT":
                self.state.exit = True            
            case "SAVE_QUIT":
                self.state.save()
                self.state.exit = True  
            case _:
                pass
        return 0

    def selected_cell(self, cell:int)->int:
        # print(f"Selected cell {cell}")  
        if self.move_sequence.get_step() == EnumEngineMoving.MS_ASW_SELECT:
            self.move_sequence.answer_select(cell)
        return 0
    
    def destinated_cell(self, index:int)->int:
        # print(f"Destinated index {index}")  
        if self.move_sequence.get_step() == EnumEngineMoving.MS_ASW_DESTINATION:
            self.move_sequence.answer_destination(index)
        return 0
    
    def terminate_move(self, move:Optional[Move])->int:
        if self.move_sequence.get_step() != EnumEngineMoving.MS_IDLE:
            if move == None:                
                self.move_sequence.set_step(EnumEngineMoving.MS_QST_SELECT)
            else:
                self.move_sequence.validated_move(move)
        return 0
    
    def game_over(self)->int:
        if self.move_sequence.get_step() != EnumEngineMoving.MS_IDLE:
            self.move_sequence.answer_game_over()
        return 0

