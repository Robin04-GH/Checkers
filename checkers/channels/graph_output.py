import enum
from typing import Protocol, Optional
from checkers.channels.shared_data import Message, SharedData
from checkers.engine.game.move import Move

# Classe usata per definire gli ID dei messaggi in arrivo al modulo grafico
# N.B.: ogni ID gestisce un metodo scrivere il messaggio nella queue (sender) ed uno leggere (receiver) !
@enum.unique
class EnumGraphOutput(enum.Enum):
    GO_NONE = 0
    GO_STRING = 1
    GO_SELECTED_CELL = 2
    GO_DESTINATED_CELL = 3
    GO_TERMINATE_MOVE = 4

# protocol
class ProtGraphOutput(Protocol):
    def print_string(string:str)->int: ...
    def selected_cell(cell:int)->int: ...
    def destinated_cell(index:int)->int: ...
    def terminate_move(move:Optional[Move])->int: ...

class GraphOutputSender:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def await_sended(self, await_id:int)->bool:
        return self._shared_data.await_sended(await_id)
    
    # Metodi del protocollo (sender)
    def print_string(self, string:str)->int:
        return self._shared_data.send(Message(EnumGraphOutput.GO_STRING.value, (string,)))

    def selected_cell(self, cell:int)->int:
        return self._shared_data.send_awaitable(Message(EnumGraphOutput.GO_SELECTED_CELL.value, (cell,)))

    def destinated_cell(self, index:int)->int:
        return self._shared_data.send_awaitable(Message(EnumGraphOutput.GO_DESTINATED_CELL.value, (index,)))

    def terminate_move(self, move:Optional[Move])->int:
        return self._shared_data.send_awaitable(Message(EnumGraphOutput.GO_TERMINATE_MOVE.value, (move,)))

class GraphOutputReceiver:
    """
    """

    def __init__(self, shared_data:SharedData):
        self._shared_data = shared_data

    def dispatcher(self, instance:ProtGraphOutput):
        _msg : Message = self._shared_data.receive(instance)

        # match metodi del protocollo (receiver)
        match _msg.id:
            case EnumGraphOutput.GO_NONE.value:
                pass
            case EnumGraphOutput.GO_STRING.value: 
                instance.print_string(_msg.data[0])
            case EnumGraphOutput.GO_SELECTED_CELL.value:
                instance.selected_cell(_msg.data[0])                
            case EnumGraphOutput.GO_DESTINATED_CELL.value:
                instance.destinated_cell(_msg.data[0])                
            case EnumGraphOutput.GO_TERMINATE_MOVE.value:
                instance.terminate_move(_msg.data[0])                
            case _:
                raise KeyError(f"GraphOutput recived {self.msg.id} not contained in messages list !")
