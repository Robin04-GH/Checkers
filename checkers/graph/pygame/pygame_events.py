import pygame
# import time
# import debugpy
# import pdb
from pygame.event import Event
from typing import Callable
from checkers.graph.pygame.pygame_state import PygameState, EnumPygameMoving, EnumEventMoves
from checkers.channels.graph_output import ProtGraphOutput
from checkers.engine.game.cells import Coordinates2D

class PygameEventManager:
    """
    Pygame event handling class:
     - system
     - mouse
     - keyboard
     - timer
    """

    def __init__(self, state:PygameState, sender : ProtGraphOutput):
        self.state : PygameState = state
        self.sender : ProtGraphOutput = sender
        self.running : bool = True
        # self._space_pressed : bool = False
        self._lalt_pressed : bool = False
        self._caps_lock : bool = False
        # self.counter : int = 0
        self.debug_event : bool = False

    def get_running(self)->bool:
        return self.running

    def dispatcher(self, events:list[Event]):
        for event in events:
            if event.type in self.handlers:
                """
                if self.debug_event:
                    # To give the debugger (VS code) time to catch the context
                    # time.sleep(0.01)
                    # To force VS code to sync the current frame
                    # debugpy.breakpoint()
                    # Integrated Python debugger inside the thread
                    # pdb.set_trace()
                """
                self.handlers[event.type](self, event)

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
        #self.debug(event)
        self.debug(f"MouseDown(X,Y)={x},{y}")

        match event.button:
            # left 
            case 1:
                self.start_moving(Coordinates2D(col=x, row=y))                
            # right
            case 3:
                if not self.state.get_pause():
                    self.state.set_pause(True)
                else:
                    self.undo()
            case 2 | _:
                pass

    def on_mouse_up(self, event:Event):
        x, y = event.pos
        self.debug(f"MouseUp(X,Y)={x},{y}")
        self.stop_moving()

    def on_mouse_motion(self, event:Event):
        x, y = event.pos
        #self.debug(f"MouseMotion(X,Y)={x},{y}")
        self.mouse_moving(Coordinates2D(col=x, row=y))

    def on_mouse_wheel(self, event:Event):
        y = event.y
        #self.debug(f"Wheel(Y)={y}")

    # Keyboard event
    def on_key_down(self, event:Event):
        if event.key == pygame.K_SPACE:
            self.debug("Pressed SPACE")
            self.continue_move()

        if event.key == pygame.K_PAUSE:
            self.debug("Pressed PAUSE")
            self.state.set_pause(True)

        elif event.key == pygame.K_TAB:
            self.debug("Pressed TAB")
            self.keyboard_selected()

        elif event.key == pygame.K_RETURN:
            self.debug("Pressed RETURN")
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
            self.undo()

        elif event.key == pygame.K_ESCAPE:
            self.debug("Pressed ESCAPE")
            self.stop_moving()

    def on_key_up(self, event:Event):
        if event.key == pygame.K_x and self._lalt_pressed:
            self.on_quit(event)

        elif event.key == pygame.K_s and self._lalt_pressed:
            self.save_and_quit(event)

        elif event.key == pygame.K_SPACE:
            self.debug("Released SPACE")

        elif event.key == pygame.K_PAUSE:
            self.debug("Released PAUSE")

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

    """
    def key_pressed(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_xxx]:
            self.debug("Hold pressed xxx")
            self._xxx_pressed = True
        else:
            self._xxx_pressed = False
    """

    def key_mods(self):
        mods = pygame.key.get_mods()
        self._caps_lock = True if mods & pygame.KMOD_CAPS else False
        self._lalt_pressed = True if mods & pygame.KMOD_LALT else False

        if self._caps_lock:
            if not self.state.get_pause():
                self.state.finaling_viewer_timer()

    def start_moving(self, coor:Coordinates2D | None = None):
        if not self.state.get_viewer_mode():
            if self.state.state_moving == EnumPygameMoving.M_SELECTION:
                if coor is not None:
                    id_dark_cell : int = self.state.get_cell_from_pos(coor)
                    self.debug(f"dark_cell={id_dark_cell}")

                if self.state.start_moving(self.state.selected_cell):
                    self.sender.selected_cell(self.state.selected_cell)
            elif self.state.get_game_over():
                self.continue_move()
        else:
            self.continue_move()

    def stop_moving(self):
        if not self.state.get_viewer_mode():
            if self.state.state_moving.value >= EnumPygameMoving.M_SELECTED.value:
                self.sender.terminate_move(self.state.stop_moving())

    def mouse_moving(self, coor:Coordinates2D):
        if not self.state.get_viewer_mode():
            if self.state.state_moving == EnumPygameMoving.M_SELECTION:
                id_dark_cell : int = self.state.get_cell_from_pos(coor)
                # self.debug(f"dark_cell={id_dark_cell}")
                self.state.set_selected_cell(id_dark_cell)
            elif self.state.state_moving == EnumPygameMoving.M_DESTINATION:
                self.state.constrain_position_mouse(coor)

    def sender_move(self, index:int):
        if index != -1:
            self.state.set_destinated_cell(index)
            if index == self.state.previous_index:
                # move cancellation
                self.sender.destinated_cell(-1)
            else:
                # move progress
                self.sender.destinated_cell(index)

    def continue_move(self):
        if self.state.get_pause():                
            self.state.set_pause(False)
        else:
            self.state.finaling_viewer_timer()

        if self.state.get_game_over():
            self.state.set_game_over(False)
            self.sender.game_over()

    def keyboard_selected(self):
        if not self.state.get_viewer_mode():
            if self.state.state_moving == EnumPygameMoving.M_SELECTION:
                id_dark_cell = self.state.get_next_selected_cell()
                self.debug(f"dark_cell={id_dark_cell}")
                self.state.set_selected_cell(id_dark_cell)

    def choose_move(self, key_idx:int):
        if not self.state.get_viewer_mode():
            if self.state.state_moving == EnumPygameMoving.M_DESTINATION:            
                self.state.set_position_keyboard(key_idx)

    def event_timer(self, elapsed:int):
        #self.counter += 1
        #print(f"Counter_timer = {self.counter}")
        self.state.scan_cell_timer()

        index = self.state.moving_timer(elapsed)
        if index != None:
            self.sender_move(index)

        match self.state.viewer_timer(elapsed):
            case EnumEventMoves.E_SELECTED:
                self.sender.selected_cell(self.state.selected_cell)
            case EnumEventMoves.E_VALIDATED:
                self.sender.terminate_move(self.state.stop_moving())
                self.state.set_viewer_mode(False)
            case _:
                pass

    def undo(self):
        if self.state.get_viewer_mode():
            self.state.set_lock(True)
            self.sender.undo()

    def save_and_quit(self, event:Event):
        self.sender.print_string(f"SAVE_QUIT")
        self.running = False

    # with global argoments : debug("message {}, {}", var1, var2)
    # with f-string style : debug(f"message {var1}, {var2})
    # Using 'kwargs' to accept named parameters as well (example dict)
    def debug(self, msg:str, *args, **kwargs):
        if self.debug_event:
            if args or kwargs:
                print(msg.format(*args, **kwargs))
            else:
                print(msg)

    handlers : dict[Event, Callable[[Event], None]] = {
        # System
        pygame.QUIT : on_quit,
        pygame.WINDOWFOCUSGAINED : on_focus_gained,
        pygame.WINDOWFOCUSLOST : on_focus_lost,
        # Mouse
        pygame.MOUSEBUTTONDOWN : on_mouse_down,
        pygame.MOUSEBUTTONUP : on_mouse_up,
        pygame.MOUSEMOTION : on_mouse_motion,
        pygame.MOUSEWHEEL : on_mouse_wheel,
        # Keyboard
        pygame.KEYDOWN : on_key_down,
        pygame.KEYUP : on_key_up,
    }

# print(event)
# <Event(1025-MouseButtonDown {'pos': (557, 197), 'button': 1, 'touch': False, 'window': None})>
# event.button == 1 click on left button
# event.button == 2 click on middle button
# event.button == 3 click on right button

# mouse_button = pygame.mouse.get_pressed()
# mouse_button[0] left button
# mouse_button[1] middle button
# mouse_button[2] right button
