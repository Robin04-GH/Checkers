# To avoid using quotes ("") in the type hints on the 'other' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from checkers.engine.game.cells import Cells, EnumMove
from checkers.constant import MAX_CELL_MOVE

# To make the class formally immutable, use @dataclass(frozen=True).
# This way, attributes cannot be modified and hashing can be used.
@dataclass(frozen=True)
class Score:
    capture_pieces : int = 0
    capture_king : int = 0
    first_capture_king : int = 0
    type_move : EnumMove = EnumMove.M_NONE
    # does not determine score, only given storage
    # N.B.: Score with only different last_capture_cell attribute are identical 
    # for the equality and hash operator !
    last_capture_cell : int = -1
    """
    Class type for move score :
    - number of capture pieces
    - number of capture king
    - step first capture king
    - type move (single/capture)
    storage last capture cell

    N.B.: lo score è uno strumento per individuare tutte le possibili mosse in base alle regole del gioco.
    L'insieme di mosse risultanti tutte con stesso score (il massimo ottenibile) sarà poi oggetto del 
    processo di inferenza !
    """

    def set_single(self)->Score:
        # Verify type_move
        if self.type_move != EnumMove.M_NONE:
            raise ValueError(f"Class Score, set_single(): error set type move !")
            
        return Score(self.capture_pieces, self.capture_king, self.first_capture_king, EnumMove.M_SIMPLE, self.last_capture_cell)

    def set_capture_man(self, last_capture_cell:int)->Score:
        return Score(self.capture_pieces + 1, self.capture_king, self.first_capture_king, EnumMove.M_CAPTURE, last_capture_cell)
    
    def set_capture_king(self, last_capture_cell:int, step:int)->Score:
        # Verify step
        if step <= 0:
            raise ValueError(f"Class Score, set_capture_king(): error set step first capture king !")
        
        return Score(self.capture_pieces + 1, self.capture_king + 1, (
            self.first_capture_king 
            if self.first_capture_king != 0 else step
        ), EnumMove.M_CAPTURE, last_capture_cell)

    def __eq__(self, other: Score)->bool:
        """
        Define == operator.

        @param other: Other score that we are comparing with.
        """

        if other != None:
            if (
                self.capture_pieces == other.capture_pieces and
                self.capture_king == other.capture_king and
                self.first_capture_king == other.first_capture_king and
                self.type_move == other.type_move
            ):
                return True
            else:
                return False

    def __lt__(self, other: Score)->bool:
        """
        Define < operator.

        @param other: Other score that we are comparing with.
        """

        if other != None:
            if self.capture_pieces != other.capture_pieces:
                if self.capture_pieces < other.capture_pieces:
                    return True
                else:
                    return False
            else:
                if self.capture_king != other.capture_king:
                    if self.capture_king < other.capture_king:
                        return True
                    else:
                        return False
                else:
                    if self.first_capture_king != other.first_capture_king:
                        if self.first_capture_king < other.first_capture_king:
                            return True
                        else:
                            return False
                    else:
                        if self.type_move.value < other.type_move.value:
                            return True                        
                        else:
                            return False

    def __gt__(self, other: Score)->bool:
        """
        Define > operator.

        @param other: Other score that we are comparing with.
        """

        if other != None:
            if self.capture_pieces != other.capture_pieces:
                if self.capture_pieces > other.capture_pieces:
                    return True
                else:
                    return False
            else:
                if self.capture_king != other.capture_king:
                    if self.capture_king > other.capture_king:
                        return True
                    else:
                        return False
                else:
                    if self.first_capture_king != other.first_capture_king:
                        if self.capture_king > other.capture_king:
                            return True
                        else:
                            return False
                    else:
                        if self.type_move.value > other.type_move.value:
                            return True
                        else:
                            return False

    # Python requires that if two objects are considered equal via the 
    # __eq__ method, then their hash value (__hash__) must be the same.
    def __hash__(self)->int:
        return hash((self.capture_pieces, self.capture_king, self.first_capture_king, self.type_move.value))

class Node:
    """
    Class type for tree of all moves related to a cell of origin
    """
    def __init__(self, index_cell:int, score:Score=Score(), previous_move:Optional[Node]=None):
        self.index_cell : int = index_cell
        self.score : Score = score
        self.prev_move : Optional[Node] = previous_move
        self.next_move : list[Optional[Node]] = []

    def is_complete_next(self)->bool:
        return len(self.next_move) == MAX_CELL_MOVE
    
    def cleanup(self):
        # recursively deletes child nodes
        for child in self.next_move:
            if child != None:
                child.cleanup()
                del child
        # remove references
        self.next_move.clear()

    def remove_child(self, ref:Node)->bool:
        if ref != None:
            for index, child in enumerate(self.next_move):
                if child == ref:
                    # recursively deletes child nodes
                    child.cleanup()
                    del child
                    # remove reference
                    self.next_move[index] = None
                    return True
        return False

# To make the class formally immutable, use @dataclass(frozen=True).
# This way, attributes cannot be modified and hashing can be used.
@dataclass(frozen=True)
class Move:
    origin : int
    destinations : tuple[int]
    captures : tuple[int] = ()
    """
    Classe tipo per rappresentare una mossa
    """

    # Il metodo '__post_init__' viene chiamato dopo la creazione dell’oggetto, 
    # quindi è il posto giusto per fare validazioni :
    #  1) la validita delle cells è considerata implicita nella costruzione precedente delle liste
    def __post_init__(self):
        # 2) verifica se captures è vuota, len destinations = 1 : caso 'move simple'
        if not self.captures:
            if len(self.destinations) != 1:
                raise ValueError(
                    f"Class Move, __post_init__(): simple move must have exactly 1 destination, got {len(self.destinations)}"
                )

        # 3) verifica se len(captures) = len(destinations) : caso 'move capture'
        else:
            if len(self.captures) != len(self.destinations):
                raise ValueError(
                    f"Class Move, __post_init__(): capture move must have same number of captures and destinations "
                    f"({len(self.captures)} != {len(self.destinations)})"
                )

    def __eq__(self, other: Move)->bool:
        """
        Define == operator.

        @param other: Other move that we are comparing with.
        """

        if other != None:
            if (
                self.origin == other.origin and
                self.destinations == other.destinations and
                self.captures == other.captures
            ):
                return True
            else:
                return False

    # Python requires that if two objects are considered equal via the 
    # __eq__ method, then their hash value (__hash__) must be the same.
    def __hash__(self)->int:
        return hash((self.origin, self.destinations, self.captures))
    
    def set_capture(self, destination:int, capture:int):
        _destinations = (*self.destinations, destination)
        _captures = (*self.captures, capture)
        return Move(self.origin, _destinations, _captures)
    
    def remove_last(self):
        _destinations = self.destinations[:-1]
        _captures = self.captures[:-1] if len(self.captures) else tuple()
        return Move(self.origin, _destinations, _captures)

"""
Note :
- la cella di origine è esterna a Move, sarà la chiave del dict che ha come value l'albero o set delle mosse.
  Questo perchè una data cella di origine (rappresenteranno la selezione mosse) è la radice dell'albero che 
  puo contenere molte mosse.
"""