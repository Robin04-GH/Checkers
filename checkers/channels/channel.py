import enum    
from checkers.channels.shared_data import SharedData
from checkers.channels.graph_input import GraphInputSender, GraphInputReceiver
from checkers.channels.graph_output import GraphOutputSender, GraphOutputReceiver
    
@enum.unique
class EnumChannelProtocols(enum.Enum):
    C_PROTGRAPHINPUT = 1
    C_PROTGRAPHOUTPUT = 2
    
_PROTOCOL_MAP = { 
    EnumChannelProtocols.C_PROTGRAPHINPUT: (GraphInputSender, GraphInputReceiver), 
    EnumChannelProtocols.C_PROTGRAPHOUTPUT: (GraphOutputSender, GraphOutputReceiver), 
}    

class Channel:
    """
    A communication channel with a sender and receiver sharing the same data.
    """ 
    
    def __init__(self, protocol: EnumChannelProtocols):
        self._shared_data = SharedData()
        
        try:
            sender_cls, receiver_cls = _PROTOCOL_MAP[protocol]
        except KeyError:
            raise ValueError(f"Unknown protocol {protocol}")
        
        self.sender = sender_cls(self._shared_data)
        self.receiver = receiver_cls(self._shared_data)
        
    def register(self, instance: any):
        self._shared_data.register(instance)
        
    def unregister(self, instance: any):
        self._shared_data.unregister(instance)

class Gateway:
    """
    Creates all communication channels defined by the available protocols.
    """ 
    
    def __init__(self):
        self.channels = { 
            protocol: Channel(protocol)
            for protocol in EnumChannelProtocols
        }        
