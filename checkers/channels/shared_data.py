import enum
import queue
import weakref
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
        self.queue = queue.Queue(MAX_QUEUE_SIZE)    
        self.lock = threading.Lock()
        # Hint: if a receiver is destroyed but not deregistered, using 'weakref' avoids memory leaks !
        self.registered_receivers = weakref.WeakSet()
        self.counters : dict[EnumQueue, int] = { EnumQueue.Q_PUSH : 0, EnumQueue.Q_POP : 0 }
        self.awaits : set[int] = set()
        self.latcher_receivers : set[any] = set()
        self.last_message : Message = Message()

    # Hint: methods for internal use of the class do not use 'lock' because it is already used 
    # by the other calling methods !
    def _has_registered_receivers(self)->bool:
        return len(self.registered_receivers) != 0
        
    def _counters_inc(self, key:EnumQueue)->int:
        self.counters[key] = (self.counters[key] % MAX_QUEUE_SIZE) + 1

        # if Q_POP updates awaits list
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
            except queue.Full:
                print(f"Full exception queue!")
        return 0

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

    def receive(self, instance: any) -> Message:
        with self.lock:
            if instance not in self.registered_receivers:
                return Message()

            # In the absence of distribution, read new message
            if not self.latcher_receivers:
                try:
                    msg = self.queue.get_nowait()
                except queue.Empty:
                    return Message()

                self.last_message = msg
                self.latcher_receivers = set(self.registered_receivers)

            # 'last_message' distribution among all registered receivers
            if instance not in self.latcher_receivers:
                return Message()

            self.latcher_receivers.remove(instance)

            # Only on the last receiver increment counters (Q_POP)
            if not self.latcher_receivers:
                self._counters_inc(EnumQueue.Q_POP)

            return self.last_message
        