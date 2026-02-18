import enum
from typing import Protocol
from checkers.types import DestCellsType
from checkers.channels.shared_data import Message, SharedData

# Classe usata per definire gli ID dei messaggi in arrivo al modulo grafico
# N.B.: ogni ID gestisce un metodo scrivere il messaggio nella queue (sender) ed uno leggere (receiver) !
@enum.unique
class EnumGraphInput(enum.Enum):
    GI_NONE = 0
    GI_STRING = 1
    GI_RESET = 2
    GI_CELL_PIECE = 3
    GI_SELECTION_CELLS = 4
    GI_DESTINATION_CELLS = 5
    GI_PROMOTED_KING = 6

# protocol
class ProtGraphInput(Protocol):
    def print_string(string:str, value:float)->int: ...
    def reset()->int: ...
    def players_pieces(self, cell_piece:tuple[int, int])->int: ...
    def selection_cells(cells:tuple[int, ...])->int: ...   
    def destination_cells(cells:DestCellsType, previous_index:int)->int: ...
    def promoted_king(cell:int)->int: ...

class GraphInputSender:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def await_sended(self, await_id:int)->bool:
        return self._shared_data.await_sended(await_id)
    
    # Metodi del protocollo (sender)
    def print_string(self, string:str, value:float)->int:
        return self._shared_data.send(Message(EnumGraphInput.GI_STRING.value, (string, value)))

    def reset(self)->int:
        return self._shared_data.send(Message(EnumGraphInput.GI_RESET.value, ()))

    def players_pieces(self, cell_piece:tuple[int, int])->int:
        return self._shared_data.send_awaitable(Message(EnumGraphInput.GI_CELL_PIECE.value, (cell_piece,)))

    def selection_cells(self, cells:tuple[int, ...])->int:
        return self._shared_data.send_awaitable(Message(EnumGraphInput.GI_SELECTION_CELLS.value, (cells,)))

    def destination_cells(self, cells:DestCellsType, previous_index:int)->int:
        return self._shared_data.send_awaitable(Message(EnumGraphInput.GI_DESTINATION_CELLS.value, (cells, previous_index)))
    
    def promoted_king(self, cell:int)->int:
        return self._shared_data.send_awaitable(Message(EnumGraphInput.GI_PROMOTED_KING.value, (cell,)))

class GraphInputReceiver:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def dispatcher(self, instance:ProtGraphInput):
        _msg : Message = self._shared_data.receive(instance)

        # match metodi del protocollo (receiver)
        match _msg.id:
            case EnumGraphInput.GI_NONE.value:
                pass
            case EnumGraphInput.GI_STRING.value: 
                instance.print_string(*_msg.data)
            case EnumGraphInput.GI_RESET.value:
                instance.reset() 
            case EnumGraphInput.GI_CELL_PIECE.value:
                instance.players_pieces(_msg.data[0])                
            case EnumGraphInput.GI_SELECTION_CELLS.value:
                instance.selection_cells(_msg.data[0])                
            case EnumGraphInput.GI_DESTINATION_CELLS.value:
                instance.destination_cells(*_msg.data) 
            case EnumGraphInput.GI_PROMOTED_KING.value:
                instance.promoted_king(*_msg.data) 
            case _:
                raise KeyError(f"GraphInput recived {self.msg.id} not contained in messages list !")
