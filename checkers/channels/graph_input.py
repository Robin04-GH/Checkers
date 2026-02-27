import enum
from typing import Protocol, Callable, Dict, Any
from checkers.types import DestCellsType
from checkers.channels.shared_data import Message, SharedData

HandlerType = Callable[["ProtGraphInput", tuple[Any, ...]], None]

# Class used to define the IDs of messages arriving at the graphics module.
# Hint: Each ID manages a method for writing the message to the queue (sender) 
# and one for reading it (receiver).
@enum.unique
class EnumGraphInput(enum.Enum):
    GI_NONE = 0
    GI_STRING = 1
    GI_RESET = 2
    GI_CELL_PIECE = 3
    GI_SELECTION_CELLS = 4
    GI_DESTINATION_CELLS = 5
    GI_PROMOTED_KING = 6

DISPATCH_GRAPH_INPUT_MAP: Dict[int, HandlerType] = {
    EnumGraphInput.GI_NONE.value: lambda inst, data: None,
    EnumGraphInput.GI_STRING.value: lambda inst, data: inst.print_string(*data),
    EnumGraphInput.GI_RESET.value: lambda inst, data: inst.reset(),
    EnumGraphInput.GI_CELL_PIECE.value: lambda inst, data: inst.players_pieces(data[0]),
    EnumGraphInput.GI_SELECTION_CELLS.value: lambda inst, data: inst.selection_cells(data[0]),
    EnumGraphInput.GI_DESTINATION_CELLS.value: lambda inst, data: inst.destination_cells(*data),
    EnumGraphInput.GI_PROMOTED_KING.value: lambda inst, data: inst.promoted_king(*data),
}

# protocol
class ProtGraphInput(Protocol):
    def print_string(self, string:str, value:float)->int: ...
    def reset(self)->int: ...
    def players_pieces(self, cell_piece:tuple[int, int])->int: ...
    def selection_cells(self, cells:tuple[int, ...])->int: ...
    def destination_cells(self, cells:DestCellsType, previous_index:int)->int: ...
    def promoted_king(self, cell:int)->int: ...

class GraphInputSender:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def await_sended(self, await_id:int)->bool:
        return self._shared_data.await_sended(await_id)
    
    def _send(self, msg_id: EnumGraphInput, *args, awaitable=False):
        msg = Message(msg_id.value, args)
        if awaitable:
            return self._shared_data.send_awaitable(msg)
        return self._shared_data.send(msg)

    # Protocol methods (sender)
    def print_string(self, string:str, value:float)->int:
        return self._send(EnumGraphInput.GI_STRING, string, value)

    def reset(self)->int:
        return self._send(EnumGraphInput.GI_RESET)

    def players_pieces(self, cell_piece:tuple[int, int])->int:
        return self._send(EnumGraphInput.GI_CELL_PIECE, cell_piece)

    def selection_cells(self, cells:tuple[int, ...])->int:
        return self._send(EnumGraphInput.GI_SELECTION_CELLS, cells)

    def destination_cells(self, cells:DestCellsType, previous_index:int)->int:
        return self._send(EnumGraphInput.GI_DESTINATION_CELLS, cells, previous_index)
    
    def promoted_king(self, cell:int)->int:
        return self._send(EnumGraphInput.GI_PROMOTED_KING, cell)

class GraphInputReceiver:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def dispatcher(self, instance:ProtGraphInput):
        msg : Message = self._shared_data.receive(instance)

        handler = DISPATCH_GRAPH_INPUT_MAP.get(msg.id)
        if handler is None:
            raise KeyError(f"Unknown message id {msg.id}")
        handler(instance, msg.data)
