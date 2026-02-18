import enum    
from checkers.channels.shared_data import SharedData
from checkers.channels.graph_input import GraphInputSender, GraphInputReceiver
from checkers.channels.graph_output import GraphOutputSender, GraphOutputReceiver
    
@enum.unique
class EnumChannelProtocols(enum.Enum):
    C_PROTGRAPHINPUT = 1
    C_PROTGRAPHOUTPUT = 2
    
class Channel:
    """
    """

    def __init__(self, protocol:EnumChannelProtocols):
        self._shared_data : SharedData = SharedData()
        match protocol:
            case EnumChannelProtocols.C_PROTGRAPHINPUT:
                self.sender : GraphInputSender = GraphInputSender(self._shared_data)   
                self.receiver : GraphInputReceiver = GraphInputReceiver(self._shared_data)
            case EnumChannelProtocols.C_PROTGRAPHOUTPUT:
                self.sender : GraphOutputSender = GraphOutputSender(self._shared_data)   
                self.receiver : GraphOutputReceiver = GraphOutputReceiver(self._shared_data)
            case _:
                raise ValueError(f"Specified name protocol {protocol} not exist !")        

    def register(self, instance:any):
        self._shared_data.register(instance)

    def unregister(self, instance:any):
        self._shared_data.unregister(instance)    

# Un gateway contiene gli oggetti comuni necessari per costruire un canale di comunicazione 
# direzionale tra le classi registrate :
#  - definizione dei messaggi
#  - una queue per direzione
class Gateway():
    """
    """ 

    def __init__(self):        
        self.graph_input : Channel = Channel(EnumChannelProtocols.C_PROTGRAPHINPUT)
        self.graph_output : Channel = Channel(EnumChannelProtocols.C_PROTGRAPHOUTPUT)
