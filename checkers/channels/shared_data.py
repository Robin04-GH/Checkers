import enum
import queue
import threading
from dataclasses import dataclass

# To make the class formally immutable, use @dataclass(frozen=True).
# This way, attributes cannot be modified and hashing can be used.
@dataclass(frozen=True)
class Message:
    """
    """
    id : int = 0
    data : tuple[any, ...] = ()

@enum.unique
class EnumQueue(enum.Enum):
    Q_PUSH = 0
    Q_POP = 1

MAX_QUEUE_SIZE = 1024

class SharedData:
    """
    """

    def __init__(self):
        self.queue = queue.Queue()    
        self.lock = threading.Lock()
        self.registered_receivers : set[any] = set()
        self.counters : dict[EnumQueue, int] = { EnumQueue.Q_PUSH : 0, EnumQueue.Q_POP : 0 }
        self.awaits : set[int] = set()
        self.latcher_receivers : set[any] = set()
        self.last_message : Message = Message()
        self.enable_get : bool = False

    # N.B.: metodi ad uso interno senza lock perchè utilizzato dai chiamanti
    def _has_registered_receivers(self)->bool:
        return len(self.registered_receivers) != 0
        
    def _counters_inc(self, key:EnumQueue)->int:
        self.counters[key] += 1 
        if self.counters[key] > MAX_QUEUE_SIZE:
            self.counters[key] -= MAX_QUEUE_SIZE
        # self.counters[key] = +1 if self.counters[key] < MAX_QUEUE_SIZE else 1

        # se Q_POP aggiorna lista awaits
        if key == EnumQueue.Q_POP:
            _n = self.counters[key] 
            if _n in self.awaits:
                self.awaits.remove(_n)

        return self.counters[key]

    def _send(self, msg:Message)->int:
        if self._has_registered_receivers():
            try:
                self.queue.put(msg, False)
                return self._counters_inc(EnumQueue.Q_PUSH)
            except:
                print(f"Full exception queue!")
        return 0
    
    def _receive_buffer(self, instance:any)->Message:
        if self.last_message != None and instance in self.latcher_receivers:
            self.enable_get = False
            self.latcher_receivers.remove(instance)

            if len(self.latcher_receivers) == 0:
                self._counters_inc(EnumQueue.Q_POP)

            return self.last_message
        else:
            return Message()

    def register(self, instance:any):
        with self.lock:
            self.registered_receivers.add(instance)

    def unregister(self, instance:any):
        with self.lock:
            if instance in self.registered_receivers:
                self.registered_receivers.remove(instance)

    def send(self, msg:Message)->int:
        with self.lock:
            return self._send(msg)

    def send_awaitable(self, msg:Message)->int:
        with self.lock:
            _ret = self._send(msg)
            if _ret > 0:
                self.awaits.add(_ret)
                return _ret
        
    def await_sended(self, await_id:int)->bool:
        with self.lock:
            if not MAX_QUEUE_SIZE >= await_id > 0:
                raise ValueError(f"Specified await ID {await_id} is out of bounds !")        
            if await_id not in self.awaits:
                return True
            else:
                return False
            
    def receive(self, instance:any)->Message:
        with self.lock:
            if instance in self.registered_receivers:
                if len(self.latcher_receivers) == 0:
                    self.latcher_receivers = self.registered_receivers.copy()
                    self.enable_get = True

                if self.enable_get:
                    try:
                        self.last_message = self.queue.get_nowait()
                    except:
                        return Message()
                    
                return self._receive_buffer(instance)
        return Message()
