import enum
from typing import Protocol, Optional, Callable, Dict, Any
from checkers.channels.shared_data import Message, SharedData
from checkers.engine.game.move import Move

HandlerType = Callable[["ProtGraphOutput", tuple[Any, ...]], None]

# Class used to define the IDs of messages sent by graphics module.
# Hint: Each ID manages a method for writing the message to the queue (sender) 
# and one for reading it (receiver).
@enum.unique
class EnumGraphOutput(enum.Enum):
    GO_NONE = 0
    GO_STRING = 1
    GO_SELECTED_CELL = 2
    GO_DESTINATED_CELL = 3
    GO_TERMINATE_MOVE = 4
    GO_GAME_OVER = 5

DISPATCH_GRAPH_OUTPUT_MAP: Dict[int, HandlerType] = {
    EnumGraphOutput.GO_NONE.value: lambda inst, data: None,
    EnumGraphOutput.GO_STRING.value: lambda inst, data: inst.print_string(data[0]),
    EnumGraphOutput.GO_SELECTED_CELL.value: lambda inst, data: inst.selected_cell(data[0]),
    EnumGraphOutput.GO_DESTINATED_CELL.value: lambda inst, data: inst.destinated_cell(data[0]),
    EnumGraphOutput.GO_TERMINATE_MOVE.value: lambda inst, data: inst.terminate_move(data[0]),
    EnumGraphOutput.GO_GAME_OVER.value: lambda inst, data: inst.game_over(),
}

# protocol
class ProtGraphOutput(Protocol):
    def print_string(self, string:str)->int: ...
    def selected_cell(self, cell:int)->int: ...
    def destinated_cell(self, index:int)->int: ...
    def terminate_move(self, move:Optional[Move])->int: ...
    def game_over(self)->int: ...

class GraphOutputSender:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def await_sended(self, await_id:int)->bool:
        return self._shared_data.await_sended(await_id)
    
    def _send(self, msg_id: EnumGraphOutput, *args, awaitable=False):
        msg = Message(msg_id.value, args)
        if awaitable:
            return self._shared_data.send_awaitable(msg)
        return self._shared_data.send(msg)

    # Protocol methods (sender)
    def print_string(self, string:str)->int:
        return self._send(EnumGraphOutput.GO_STRING, string)

    def selected_cell(self, cell:int)->int:
        return self._send(EnumGraphOutput.GO_SELECTED_CELL, cell)

    def destinated_cell(self, index:int)->int:
        return self._send(EnumGraphOutput.GO_DESTINATED_CELL, index)

    def terminate_move(self, move:Optional[Move])->int:
        return self._send(EnumGraphOutput.GO_TERMINATE_MOVE, move)
    
    def game_over(self)->int:
        return self._send(EnumGraphOutput.GO_GAME_OVER)

class GraphOutputReceiver:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def dispatcher(self, instance:ProtGraphOutput):
        msg : Message = self._shared_data.receive(instance)

        handler = DISPATCH_GRAPH_OUTPUT_MAP.get(msg.id)
        if handler is None:
            raise KeyError(f"Unknown message id {msg.id}")
        handler(instance, msg.data)
