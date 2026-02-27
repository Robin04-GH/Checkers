# To avoid using quotes ("") in the type hints on the 'other' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
import enum, math
from checkers.types import DestCellsType
from checkers.engine.game.cells import Coordinates2D

from typing import Tuple, NamedTuple, Optional
DestCentersType = Tuple[
    Optional[Coordinates2D], Optional[Coordinates2D], Optional[Coordinates2D], Optional[Coordinates2D]
]

class Vectors2D(NamedTuple):
    x:float
    y:float

    def _add__(self, other:Vectors2D)->Vectors2D:
        return Vectors2D(self.x + other.x, self.y + other.y)
    
    def __iadd__(self, other:Vectors2D)->Vectors2D:
        return Vectors2D(self.x + other.x, self.y + other.y)

# Class to define the state of the pieces
@enum.unique
class EnumPygameMoving(enum.Enum):
    M_IDLE = 0
    M_SELECTION = 1
    M_SELECTED = 2
    M_DESTINATION = 3
    M_DESTINATED = 4

class MovingState:
    """
    Temporary data class during piece movement for possible recovery.
    The board state is updated only after validation.
    """
    
    def __init__(self):
        self.state_moving : EnumPygameMoving = EnumPygameMoving.M_IDLE
        self.selection_cells : tuple[int, ...] = ()
        self.selected_cell : int = -1
        self.actual_cell : int = -1
        self.destination_cells : DestCellsType = (-1, -1, -1, -1)
        self.previous_index : int = -1
        self.move_destinations : list[int] = []
        self.move_captures : list[int] = []                

class Filter:
    """
    A class for filtering the target position of the workpiece.
    It offers various techniques.
    """

    def __init__(self):
        self._coor_filtered : Optional[Coordinates2D] = None
        self._speed_filtered : NamedTuple = Vectors2D(0, 0)

    def init_coor_filtered(self, point:Coordinates2D):
        self._coor_filtered = point
        self._speed_filtered = Vectors2D(0, 0)

    def get_coor_filtered(self)->Coordinates2D:
        return self._coor_filtered

    def constrain_filtered(self, coor_constrained:Coordinates2D):
        _incr : Coordinates2D = Coordinates2D(
            (coor_constrained.x - self._coor_filtered.x) * 0.30,
            (coor_constrained.y - self._coor_filtered.y) * 0.30
        )
        self._coor_filtered += _incr

    def smoothing_filtered(self, coor_constrained:Coordinates2D):
        alpha = 0.25  # smaller = softer
        pos_x = self._coor_filtered.x * (1 - alpha) + coor_constrained.x * alpha
        pos_y = self._coor_filtered.y * (1 - alpha) + coor_constrained.y * alpha
        self._coor_filtered = Coordinates2D(pos_x, pos_y)

    def speed_clamp_filtered(self, coor_constrained:Coordinates2D):
        dx = coor_constrained.x - self._coor_filtered.x
        dy = coor_constrained.y - self._coor_filtered.y
        dist = math.hypot(dx, dy)
        max_speed = 12  # pixels per frame
        if dist > max_speed:
            scale = max_speed / dist
            dx *= scale
            dy *= scale
        self._coor_filtered += Coordinates2D(dx, dy)

    def critically_damped_spring(self, coor_constrained:Coordinates2D, elapsed:int):
        # parameters
        stiffness = 200.0
        damping = 2.0 * math.sqrt(stiffness)  # critical smoothing
        # _damping = 1.2 * math.sqrt(_stiffness)  # elastic spring
        dt = elapsed / 1000.0
        # strenght toward the target
        fx = stiffness * (coor_constrained.x - self._coor_filtered.x)
        fy = stiffness * (coor_constrained.y - self._coor_filtered.y)
        # update velocity
        inc_speed = Vectors2D(
            (fx - damping * self._speed_filtered.x) * dt,
            (fy - damping * self._speed_filtered.y) * dt
        )
        self._speed_filtered += inc_speed
        # update position
        inc_coor = Coordinates2D(
            self._speed_filtered.x * dt,
            self._speed_filtered.y * dt
        )
        self._coor_filtered += inc_coor

    def clamp(self, value:float, min_value:float, max_value:float)->float:
        return max(min_value, min(value, max_value))

    # linear interpolation
    def lerp(self, a:float, b:float, t:float):
        return a + (b - a) * t

    def easy_in_out_quad(self, t:float)->float:
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2

    def easing_filtered(self, coor_constrained:Coordinates2D, t:float):
        # t = self.clamp(dist / max_dist, 0, 1)
        ease = t*t*(3 - 2*t)  # smoothstep
        # _ease = self.easy_in_out_quad(t)
        pos_coor = Coordinates2D(
            round(self.lerp(self._coor_filtered.x, coor_constrained.x, ease)),
            round(self.lerp(self._coor_filtered.y, coor_constrained.y, ease))
        )
        self._coor_filtered = pos_coor

class Constrain(MovingState, Filter):
    """
    Class that constrains the movements of pieces during the move
    """
    
    def __init__(self):
        super().__init__()
        self._actual_center : Optional[Coordinates2D] = None
        self._destination_centers : DestCentersType = (None, None, None, None)
        self._coor_constrained : Optional[Coordinates2D] = None
        self._coef_constrained : Optional[float] = None

    def set_actual_center(self, actual_center:Coordinates2D):
        self._actual_center = actual_center

    def set_destination_centers(self, destination_center:DestCentersType):
        self._destination_centers = destination_center

    def init_coordinates(self, point:Coordinates2D):
        self._coor_constrained = point
        self._coef_constrained = 0
        self.init_coor_filtered(point)

    def set_coor_constrained(self, point:Coordinates2D):
        self._coor_constrained = point
        self._coef_constrained = 1

    def get_coor_constrained(self)->Coordinates2D:
        return self._coor_constrained

    def get_coef_constrained(self)->float:
        return self._coef_constrained

    # Demultiplier with min/max coordinate ratio module
    @staticmethod
    def _normalization(point:Coordinates2D)->float:
        if point.x == 0 or point.y == 0:
            return 0.0

        abs_point = Coordinates2D(abs(point.x), abs(point.y))
        min = min(abs_point.x, abs_point.y)
        max = max(abs_point.x, abs_point.y)
        return min / max

    # Point O (origin), Point D (destination), Point M (mouse)  
    # Find the projection of M on the line OD clamped inside the segment [0 <= t <= 1],
    # that is, the point of the segment closest to M.
    # Hint: the coordinates D and M are relative to those of O !
    @staticmethod
    def _closest_point_on_segment_relative(d:Coordinates2D, m:Coordinates2D)->tuple[Coordinates2D, float]:
        if d.x == 0 and d.y == 0:
            return (0, 0)

        d2 = d.x*d.x + d.y*d.y
        t = ((m.x*d.x + m.y*d.y) / d2)
        # clamp and normalization
        t = max(0.0, min(1.0, t)) # * Constrain._normalization(m)
        return Coordinates2D(round(t * d.x), round(t * d.y)), t

    def constrain_cartesian_dial(self, pixel:Coordinates2D)->int:
        if pixel.x == self._actual_center.x or pixel.y == self._actual_center.y:
            return -1
        
        if pixel.x > self._actual_center.x:
            if pixel.y < self._actual_center.y:
                # 1° dials
                return 0
            else:
                # 4° dials
                return 3
        else:
            if pixel.y < self._actual_center.y:
                # 2° dials
                return 1
            else:
                # 3° dials
                return 2
            
    def constrain_position_mouse(self, pixel:Coordinates2D):
        index : int = self.constrain_cartesian_dial(pixel)
        if index < 0:
            self._coor_constrained = self._actual_center
            return

        d = self._destination_centers[index]
        if d == None:
            self._coor_constrained = self._actual_center
            return

        d_rel = d.__sub__(self._actual_center)
        m_rel = pixel.__sub__(self._actual_center)
        coor, t = Constrain._closest_point_on_segment_relative(d_rel, m_rel)
        self._coor_constrained = coor.__add__(self._actual_center)
        self._coef_constrained = t
        