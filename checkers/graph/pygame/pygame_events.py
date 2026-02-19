import pygame
# import time
# import debugpy
# import pdb
from pygame.event import Event
from typing import Callable
from checkers.graph.pygame.pygame_state import PygameState, EnumPygameMoving
from checkers.channels.graph_output import ProtGraphOutput
from checkers.engine.game.cells import Coordinates2D

class PygameEventManager:
    """
    """

    def __init__(self, state:PygameState, sender : ProtGraphOutput):
        self.state : PygameState = state
        self.sender : ProtGraphOutput = sender
        self.running = True
        self._lalt_pressed : False
        self.debug_event : bool = True
        self.counter : int = 0

    def get_running(self)->bool:
        return self.running

    def dispatcher(self, events:list[Event]):
        for event in events:
            if event.type in self._handlers:
                if self.debug_event:
                    # Per dare tempo al debugger di agganciare il contesto
                    # time.sleep(0.01)
                    # Per forzare VS code a sincronizzare il frame corrente
                    # debugpy.breakpoint()
                    # Debugger integrato di Python dentro il thread
                    # pdb.set_trace()
                    self._handlers[event.type](self, event)

    # System event
    def on_quit(self, event:Event):
        self.sender.print_string(f"QUIT")
        self.running = False

    def on_focus_gained(self, event:Event):
        self.debug(f"Generic event : WINDOWFOCUSGAINED")

    def on_focus_lost(self, event:Event):
        self.debug(f"Generic event : WINDOWFOCUSLOST")

    # Mouse event
    def on_mouse_down(self, event:Event):
        x, y = event.pos
        self.debug(f"MouseDown(X,Y)={x},{y}")

        if self.state.state_moving is EnumPygameMoving.M_SELECTION:
            _id_dark_cell : int = self.state.get_cell_from_pos(Coordinates2D(col=x, row=y))
            self.debug(f"dark_cell={_id_dark_cell}")
            self.start_moving()

    def on_mouse_up(self, event:Event):
        x, y = event.pos
        self.debug(f"MouseUp(X,Y)={x},{y}")
        self.stop_moving()

    def on_mouse_motion(self, event:Event):
        x, y = event.pos
        #self.debug(f"MouseMotion(X,Y)={x},{y}")
        
        if self.state.state_moving is EnumPygameMoving.M_SELECTION:
            _id_dark_cell : int = self.state.get_cell_from_pos(Coordinates2D(col=x, row=y))
            # self.debug(f"dark_cell={_id_dark_cell}")
            self.state.set_selected_cell(_id_dark_cell)
        elif self.state.state_moving is EnumPygameMoving.M_DESTINATION:
            self.state.constrain_position_mouse(Coordinates2D(col=x, row=y))

    # Keyboard event
    def on_key_down(self, event:Event):
        if event.key == pygame.K_SPACE:
            self.debug("Pressed SPACE")
        elif event.key == pygame.K_TAB:
            self.debug("Pressed TAB")
            if self.state.state_moving is EnumPygameMoving.M_SELECTION:
                _id_dark_cell = self.state.get_next_selected_cell()
                self.debug(f"dark_cell={_id_dark_cell}")
                self.state.set_selected_cell(_id_dark_cell)
        elif event.key == pygame.K_RETURN:
            self.debug("Pressed RETURN")
            if self.state.state_moving is EnumPygameMoving.M_SELECTION:
                self.start_moving()
        elif event.key == pygame.K_1:
            self.debug("Pressed 1")
            self.choose_move(0)
        elif event.key == pygame.K_2:
            self.debug("Pressed 2")
            self.choose_move(1)
        elif event.key == pygame.K_3:
            self.debug("Pressed 3")
            self.choose_move(2)
        elif event.key == pygame.K_4:
            self.debug("Pressed 4")
            self.choose_move(3)
        elif event.key == pygame.K_BACKSPACE:
            self.debug("Pressed BACKSPACE")
        elif event.key == pygame.K_ESCAPE:
            self.debug("Pressed ESCAPE")
            self.stop_moving()

    def on_key_up(self, event:Event):
        if event.key == pygame.K_x and self._lalt_pressed:
            self.on_quit(event)
        elif event.key == pygame.K_SPACE:
            self.debug("Released SPACE")
        elif event.key == pygame.K_TAB:
            self.debug("Released TAB")
        elif event.key == pygame.K_RETURN:
            self.debug("Released RETURN")
        elif event.key == pygame.K_1:
            self.debug("Released 1")
        elif event.key == pygame.K_2:
            self.debug("Released 2")
        elif event.key == pygame.K_3:
            self.debug("Released 3")
        elif event.key == pygame.K_4:
            self.debug("Released 4")
        elif event.key == pygame.K_BACKSPACE:
            self.debug("Released BACKSPACE")
        elif event.key == pygame.K_ESCAPE:
            self.debug("Released ESCAPE")

    def key_pressed(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LALT]:
            self.debug("ALT (Left) tenuto premuto")
            self._lalt_pressed = True
        else:
            self._lalt_pressed = False

    def start_moving(self):
        if self.state.start_moving(self.state.selected_cell):
            self.sender.selected_cell(self.state.selected_cell)

    def stop_moving(self):
        if self.state.state_moving.value >= EnumPygameMoving.M_SELECTED.value:
            self.sender.terminate_move(self.state.stop_moving())

    def sender_move(self, index:int):
        if index != -1:
            self.state.set_destinated_cell(index)
            if index == self.state.previous_index:
                # annullamento mossa
                self.sender.destinated_cell(-1)
            else:
                # avanzamento mossa
                self.sender.destinated_cell(index)

    def choose_move(self, key_idx:int):
        if self.state.state_moving is EnumPygameMoving.M_DESTINATION:            
            self.state.set_position_keyboard(key_idx)

    def event_timer(self, elapsed:int):
        #self.counter += 1
        #print(f"Counter_timer = {self.counter}")
        self.state.scan_cell_timer()

        _index = self.state.moving_timer(elapsed)
        if _index != None:
            self.sender_move(_index)

    # con argomenti globali : debug("message {}, {}", var1, var2)
    # con stile f-string : debug(f"message {var1}, {var2})
    # Con kwargs per accettare anche parametri nominati (esempio dict)
    def debug(self, msg:str, *args, **kwargs):
        if self.debug_event:
            if args or kwargs:
                print(msg.format(*args, **kwargs))
            else:
                print(msg)

    _handlers : dict[Event, Callable[[Event], None]] = {
        # System
        pygame.QUIT : on_quit,
        pygame.WINDOWFOCUSGAINED : on_focus_gained,
        pygame.WINDOWFOCUSLOST : on_focus_lost,
        # Mouse
        pygame.MOUSEBUTTONDOWN : on_mouse_down,
        pygame.MOUSEBUTTONUP : on_mouse_up,
        pygame.MOUSEMOTION : on_mouse_motion,
        # Keyboard
        pygame.KEYDOWN : on_key_down,
        pygame.KEYUP : on_key_up,
    }
