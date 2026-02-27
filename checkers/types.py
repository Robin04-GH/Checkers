from pygame import Color, Rect
from typing import Union, Tuple
from pygame.event import Event


# Alias ​​for using the pygame.Color type in its possible representations
ColorType = Union[Color, Tuple[int, int, int], Tuple[int, int, int, int], str]
RectType = Union[Rect, Tuple[int, int, int, int]]
EventType = Tuple[Event, ...]

DestCellsType = Tuple[int, int, int, int]
