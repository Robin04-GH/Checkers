# To avoid using quotes ("") in the type hints on the 'other' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
import enum, math
from dataclasses import dataclass
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

# Classe per definire lo stato dei pezzi
@enum.unique
class EnumPygameMoving(enum.Enum):
    M_IDLE = 0
    M_SELECTION = 1
    M_SELECTED = 2
    M_DESTINATION = 3
    M_DESTINATED = 4

#@dataclass
class MovingState:

    def __init__(self):
        super().__init__()
        self.state_moving : EnumPygameMoving = EnumPygameMoving.M_IDLE
        self.selection_cells : tuple[int, ...] = ()
        self.selected_cell : int = -1
        self.actual_cell : int = -1
        self.destination_cells : DestCellsType = (-1, -1, -1, -1)
        self.previous_index : int = -1
        self.move_destinations : list[int] = []
        self.move_captures : list[int] = []                

    # Per essere cooperativa
    #def __post_init__(self):
    #    super().init__()

class Filter:
    """
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
            (coor_constrained.x - self._coor_filtered.x) * 0.75,
            (coor_constrained.y - self._coor_filtered.y) * 0.75
        )
        self._coor_filtered += _incr

    def smoothing_filtered(self, coor_constrained:Coordinates2D):
        _alpha = 0.50  # più piccolo = più morbido
        _pos_x = self._coor_filtered.x * (1 - _alpha) + coor_constrained.x * _alpha
        _pos_y = self._coor_filtered.y * (1 - _alpha) + coor_constrained.y * _alpha
        self._coor_filtered = Coordinates2D(_pos_x, _pos_y)

    def speed_clamp_filtered(self, coor_constrained:Coordinates2D):
        _dx = coor_constrained.x - self._coor_filtered.x
        _dy = coor_constrained.y - self._coor_filtered.y
        _dist = math.hypot(_dx, _dy)
        _max_speed = 4  # pixel per frame
        if _dist > _max_speed:
            _scale = _max_speed / _dist
            _dx *= _scale
            _dy *= _scale
        self._coor_filtered += Coordinates2D(_dx, _dy)

    def critically_damped_spring(self, coor_constrained:Coordinates2D, elapsed:int):
        # parameters
        _stiffness = 16.0
        _damping = 1.4 * math.sqrt(_stiffness)  # critical smoothing
        # _damping = 1.2 * math.sqrt(_stiffness)  # elastic spring
        _dt = elapsed / 1000.0
        # strenght toward the target
        _fx = _stiffness * (coor_constrained.x - self._coor_filtered.x)
        _fy = _stiffness * (coor_constrained.y - self._coor_filtered.y)
        # update velocity
        _inc_speed = Vectors2D(
            (_fx - _damping * self._speed_filtered.x) * _dt,
            (_fy - _damping * self._speed_filtered.y) * _dt
        )
        self._speed_filtered += _inc_speed
        # update position
        _inc_coor = Coordinates2D(
            self._speed_filtered.x * _dt,
            self._speed_filtered.y * _dt
        )
        self._coor_filtered += _inc_coor

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
        # _t = self.clamp(dist / max_dist, 0, 1)
        _ease = t*t*(3 - 2*t)  # smoothstep
        # _ease = self.easy_in_out_quad(t)
        _pos_coor = Coordinates2D(
            round(self.lerp(self._coor_filtered.x, coor_constrained.x, _ease)),
            round(self.lerp(self._coor_filtered.y, coor_constrained.y, _ease))
        )
        self._coor_filtered = _pos_coor

class Constrain(MovingState, Filter):
    """
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

    # demoltiplicatore con modulo del rapporto coordinate min/max
    @staticmethod
    def _normalization(point:Coordinates2D)->float:
        if point.x == 0 or point.y == 0:
            return 0.0

        _abs_point = Coordinates2D(abs(point.x), abs(point.y))
        _min = min(_abs_point.x, _abs_point.y)
        _max = max(_abs_point.x, _abs_point.y)
        return _min / _max

    # Point O (origin), Point D (destination), Point M (mouse)    
    # Trovare la proiezione di M sulla retta OD clampata all’interno del segmento [0 <= t <= 1], 
    # ovvero il punto del segmento più vicino ad M.
    # N.B.: le coordinate D ed M sono passate in relativo rispetto al quelle di O !
    @staticmethod
    def _closest_point_on_segment_relative(d:Coordinates2D, m:Coordinates2D)->tuple[Coordinates2D, float]:
        if d.x == 0 and d.y == 0:
            return (0, 0)

        _d = d.x*d.x + d.y*d.y
        _t = ((m.x*d.x + m.y*d.y) / _d)
        # clamp and normalization
        _t = max(0.0, min(1.0, _t)) # * Constrain._normalization(m)
        return Coordinates2D(round(_t * d.x), round(_t * d.y)), _t

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
        _index : int = self.constrain_cartesian_dial(pixel)
        if _index < 0:
            self._coor_constrained = self._actual_center
            return

        _d = self._destination_centers[_index]
        if _d == None:
            self._coor_constrained = self._actual_center
            return

        _d_rel = _d.__sub__(self._actual_center)
        _m_rel = pixel.__sub__(self._actual_center)
        _coor, _t = Constrain._closest_point_on_segment_relative(_d_rel, _m_rel)
        self._coor_constrained = _coor.__add__(self._actual_center)
        self._coef_constrained = _t
        # self._coor_constrained = Constrain._closest_point_on_segment_relative(_d_rel, _m_rel).__add__(self._actual_center)
        