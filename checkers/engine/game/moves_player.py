from typing import Optional
from checkers.constant import MAX_CELL_MOVE
from checkers.checkers_types import DestCellsType
from checkers.engine.game.state import State
from checkers.engine.game.move_rules import MoveRules
from checkers.engine.game.move import Score, Node, Move, EnumMove
from checkers.engine.game.cells import Cells

from checkers.constant import CHECK_TREE
if CHECK_TREE:
  from tests.check_tree import CheckTree

class MovesPlayer(MoveRules):
    """
    Class that scans all the pieces of the player_turn in the thread engine 
    to build the dict of all possible moves (local score dict)
    """

    def __init__(self, state:State):
        """
        Constructor 

        @param -: .
        """
        super().__init__(state)
        self.state = state
        self.pieces = self.state.pieces
        self._moves_dict : dict[int, tuple[Node, set[Move]]]= {}
        self._actual_origin : Optional[int] = None
        self._actual_node : Optional[Node] = None
        self._actual_move : Optional[Move] = None
    
    def __enter__(self):
        dict_score : Score = Score()
        origin_is_king : bool = False
        # iteration player's pieces
        for origin_cell in self.pieces.iter_player_cells(self.state.player_turn):                        
            # tree of possible moves to the cell of origin
            root, set_move = self.move_tree_builder(origin_cell)

            if root != None:
                # test score
                if root.score < dict_score:
                    root.cleanup()
                    del root
                else:
                    _is_king = self.state.pieces.is_king(origin_cell)
                    if (
                        root.score > dict_score or
                        (dict_score.capture_pieces > 0 and _is_king > origin_is_king)
                    ):
                        dict_score = root.score
                        origin_is_king = _is_king
                        self.reset_dict()                        
                        self._moves_dict[origin_cell] = (root, set_move)
                    # With the same score I have to capture with the strongest original cell
                    elif dict_score.capture_pieces == 0 or _is_king == origin_is_king:
                        self._moves_dict[origin_cell] = (root, set_move)

                    if CHECK_TREE:
                        ct : CheckTree = CheckTree()
                        ct.test_tree(root, set_move)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset_dict()

    def reset_dict(self):
        for (root, _) in self._moves_dict.values():
            root.cleanup()
            # del root  # Useless: only deletes the root local variable !
        self._moves_dict.clear()
        
    def reset_move(self):
        self._actual_origin = None
        self._actual_node = None
        self._actual_move = None

    def get_all_moves(self)->set[Move]:
        set_moves : set[Move] = set()
        for key in self._moves_dict:
            set_moves.update(self._moves_dict[key][1])
        return set_moves

    def get_all_keys(self)->tuple[int, ...]:
        list_keys : list[int] = []
        for key in self._moves_dict.keys():
            list_keys.append(key)
        return tuple(list_keys)  

    def initialize_move(self, origin_cell:int):
        self._actual_origin = origin_cell
        self._actual_node = self._moves_dict[origin_cell][0]
        self._actual_move = None

    # Returns a tuple (_dest_cells) with the indices of all destination cells 
    # including the previous one, identifiable by the index on the tuple (_previous_index)
    def get_destination_cells(self)->tuple[DestCellsType, int]:        
        _previous_index : int = -1
        _previous_cell : int = -1
        if self._actual_node.prev_move != None:
            _previous_cell = self._actual_node.prev_move.index_cell
            _cells : DestCellsType = Cells.get_moves(self._actual_node.index_cell, self._actual_node.score.type_move)
            try:
                _previous_index = _cells.index(_previous_cell)
            except ValueError:
                raise ValueError(f"Class MovesPlayer, get_destination_cells(): error previous index missing !")

        dest_cells : list[int] = []
        if len(self._actual_node.next_move) != MAX_CELL_MOVE:
            raise ValueError(f"Class MovesPlayer, get_destination_cells() : next_move size different from MAX_CELL_MOVE !")
        for index, _node in enumerate(self._actual_node.next_move):
            cell = _node.index_cell if _node != None else -1
            dest_cells.append(cell) if index != _previous_index else dest_cells.append(_previous_cell)

        return (tuple(dest_cells), _previous_index)
    
    def upgrade_move(self, index:int):
        if index != -1:
            # Progress
            next_node : Optional[Node] = self._actual_node.next_move[index]
            if next_node == None:
                raise ValueError(f"Class MovesPlayer, upgrade_move() : advanced move without node !")
            self._actual_node = next_node
            
            if self._actual_move == None:
                self._actual_move = Move(
                    self._actual_origin, 
                    (self._actual_node.index_cell,),
                    (self._actual_node.score.last_capture_cell,) 
                    if self._actual_node.score.type_move == EnumMove.M_CAPTURE
                    else tuple()
                )
            else:                
                self._actual_move = self._actual_move.set_capture(self._actual_node.index_cell, self._actual_node.score.last_capture_cell)
            
        else:
            # Annulment
            prev_node : Optional[Node] = self._actual_node.prev_move
            if prev_node == None:
                raise ValueError(f"Class MovesPlayer, upgrade_move() : cancel move without node")
            self._actual_node = prev_node
            
            if self._actual_node.prev_move == None:
                self._actual_move = None
            else:
                self._actual_move = self._actual_move.remove_last()
    
    def finalize_move(self, move:Move)->bool:
        print(f"{move.__repr__(self.state.number_move, self.state.player_turn)}")

        if self._actual_move != move:
            raise ValueError(f"Class MovesPlayer, finalize_move() : unsynchronized move !")        
        
        # Status update
        is_promoted_king : bool = self.state.update(move)
        self.reset_move()
        return is_promoted_king
