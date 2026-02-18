import enum
from dataclasses import dataclass
from checkers.types import DestCellsType
from checkers.engine.game.cells import Coordinates2D

from typing import Tuple, Optional
DestCentersType = Tuple[
    Optional[Coordinates2D], Optional[Coordinates2D], Optional[Coordinates2D], Optional[Coordinates2D]
]

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

class Constrain(MovingState):

    def __init__(self):
        super().__init__()
        self._actual_center : Optional[Coordinates2D] = None
        self._destination_centers : DestCentersType = (None, None, None, None)
        self._pos_x : float = 0.0
        self._pos_y : float = 0.0

    def set_actual_center(self, actual_center:Coordinates2D):
        self._actual_center = actual_center
        self._pos_x = actual_center.x
        self._pos_y = actual_center.y

    def set_destination_centers(self, destination_center:DestCentersType):
        self._destination_centers = destination_center

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
    def _closest_point_on_segment_relative(d:Coordinates2D, m:Coordinates2D)->Coordinates2D:
        if d.x == 0 and d.y == 0:
            return (0, 0)

        _d = d.x*d.x + d.y*d.y
        _t = ((m.x*d.x + m.y*d.y) / _d)
        # clamp and normalization
        _t = max(0.0, min(1.0, _t)) * Constrain._normalization(m)
        return Coordinates2D(round(_t * d.x), round(_t * d.y))

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
            
    def constrain_position(self, pixel:Coordinates2D)->Coordinates2D:
        _index : int = self.constrain_cartesian_dial(pixel)
        if _index < 0:
            return self._actual_center

        _d = self._destination_centers[_index]
        if _d == None:
            return self._actual_center

        _d_rel = _d.__sub__(self._actual_center)
        _m_rel = pixel.__sub__(self._actual_center)
        return Constrain._closest_point_on_segment_relative(_d_rel, _m_rel).__add__(self._actual_center)

    def constrain_filtered(self, pixel:Coordinates2D)->Coordinates2D:
        self._pos_x += (pixel.x - self._pos_x) * 0.3
        self._pos_y += (pixel.y - self._pos_y) * 0.3
        return Coordinates2D(round(self._pos_x), round(self._pos_y))
