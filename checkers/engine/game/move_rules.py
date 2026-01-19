from typing import Optional, Set, Tuple, List
from checkers.engine.game.cells import Cells
from checkers.engine.game.pieces import Pieces
from checkers.engine.game.state import State
from checkers.engine.game.move import Score, Node

class MoveRules(Node):
    """
    Class that builds the set of all moves allowed by the rules of the game
    in the current state starting from the cell of origin
    """

    def __init__(self, state: State):
        super().__init__(state)
        self.state = state
        self.pieces = self.state.pieces
        self.var_reset_tree()

    def var_reset_tree(self):
        self._current_node : Optional[Node] = None
        self._current_move : list[int] = []
        # cells with opposing pieces caught in the move 
        self._list_capture : list[int] = []
        # number of cells that make up the current move.
        # This value is incremented for each cell added during the construction of the tree.
        self._move_length : int = 0
        # stores the number of steps of the move before starting to explore a new alternative 
        # branch in the move tree.
        # Used to determine if a new validation node has been found and in backtracking.
        self._branch_anchor: int = 0

    # It depends only on origin_cell and player_turn, so mask is the same for the whole tree
    def set_mask(self, origin_cell:int)->tuple[bool, bool, bool, bool]:
        if self.pieces.is_man(origin_cell):
            if self.state.player_turn == Pieces.EnumPlayersColor.P_LIGHT:
                return (True, True, False, False)
            else:
                return (False, False, True, True)
        else:
            return (True, True, True, True)

    def is_empty_capture(self, capture_cell:int, origin_cell:int)->bool:
        return self.pieces.get_id_piece(capture_cell) == 0 or capture_cell == origin_cell
    
    def is_busy_single(self, single_cell:int)->bool:        
        return self.pieces.get_id_piece(single_cell) != 0 and not single_cell in self._list_capture
    
    def back_move(self, delete:bool):
        while (self._current_node.prev_move != None and 
               self._current_node.is_complete_next() and
               (not delete or self._move_length > self._branch_anchor)
        ):
            if self._list_capture:
                self._list_capture.pop()
            last_child = self._current_node
            self._current_node = self._current_node.prev_move
            if delete:
                self._current_node.remove_child(last_child)
            del self._current_move[-1]
            self._move_length -= 1
            # if cancellation of the last branch is conclused, nodes must no longer be deleted
            if self._move_length == self._branch_anchor:
                delete = False

    def delete_previous_tree(self, root:Node):
        local_node = root
        while (local_node.next_move[-1] != None):
            for local_child in local_node.next_move[:-1]:
                local_node.remove_child(local_child)
            local_node = local_node.next_move[-1]

    # tree construction with iterative method
    def move_tree_builder(self, origin_cell:int)->Tuple[Optional[Node], Set]:
        self.var_reset_tree()

        tree_root : Optional[Node] = Node(origin_cell)
        self._current_node = tree_root

        set_move : set[tuple[int, ...]] = set()

        next_node : Node = None
        mask_move : tuple[bool, bool, bool, bool] = self.set_mask(origin_cell)
        tree_score : Score = Score()
        count_move : int = 0

        # loop tree
        while self._current_node != tree_root or not self._current_node.is_complete_next():
            # loop dir
            while not self._current_node.is_complete_next():
                next_node = None
                index_dir = len(self._current_node.next_move)
                single_cell = self.pieces.get_simple_moves(self._current_node.index_cell, mask_move)[index_dir]
                if (not self.pieces.is_valid_cell(single_cell) or 
                    self._current_node.score.type_move == Cells.EnumMove.M_SIMPLE
                ):
                    self._current_node.next_move.append(None)
                else:
                    if not self.is_busy_single(single_cell):
                        if self._current_node.score.type_move == Cells.EnumMove.M_NONE:
                            # single move
                            next_node = self._add_node(Cells.EnumMove.M_SIMPLE, single_cell, None)
                        else:
                            self._current_node.next_move.append(None)
                    else:
                        capture_cell = self.pieces.get_capture_moves(self._current_node.index_cell, mask_move)[index_dir]                
                        if (not self.pieces.is_valid_cell(capture_cell) or
                            not self.is_empty_capture(capture_cell, origin_cell) or
                            self.state.pieces.get_player(single_cell) == self.state.player_turn
                        ):                            
                            self._current_node.next_move.append(None)
                        else:
                            # capture move
                            next_node = self._add_node(Cells.EnumMove.M_CAPTURE, single_cell, capture_cell)
                
                if next_node != None:
                    # look for any other steps in the move
                    self._current_node = next_node

            # move over
            if next_node != None:
                raise ValueError(f"Error in move_tree_builder() : next_node not None !")

            # move validation 
            delete : bool = False
            if self._move_length > self._branch_anchor:
                if self._current_node.score < tree_score:
                    # delete current move from tree
                    delete = True
                elif self._current_node.score > tree_score:
                    count_move =  1
                    tree_score = self._current_node.score
                    # delete tree except current move
                    self.delete_previous_tree(tree_root) 
                    set_move.clear()
                elif self._move_length > 0:
                    count_move += 1

                if not delete:
                    set_move.add(tuple(self._current_move))

            self.back_move(delete)
            # reset of self._branch_anchor needed after self.back_move() because used within the method
            self._branch_anchor = self._move_length

        # tree score storage
        tree_root.score = tree_score
        if tree_root.score.type_move == Cells.EnumMove.M_NONE:
            tree_root = None

        return (tree_root, set_move)

    def _score_node(self, type:Cells.EnumMove)->Score:
        if type == Cells.EnumMove.M_NONE:
            raise ValueError(f"Error : nothing type in _score_node() method !")
        
        if type == Cells.EnumMove.M_SIMPLE:
            return self._current_node.score.set_single()
        else:
            # Verify list capture
            if len(self._list_capture) == 0:
                raise ValueError(f"Error : _list_capture[] empty in _score_node() method !")

            capture_cell = self._list_capture[-1]

            # Verify player
            if self.state.pieces.get_player(capture_cell) == self.state.player_turn:
                raise ValueError(f"Error player capture piece in _score_node() method !")

            if self.pieces.is_man(capture_cell):
                return self._current_node.score.set_capture_man(capture_cell)
            else:
                return self._current_node.score.set_capture_king(capture_cell, self._move_length)
    
    def _add_node(self, type:Cells.EnumMove, single_cell:int, capture_cell:Optional[int]=None)->Node:
        self._move_length += 1

        if type == Cells.EnumMove.M_CAPTURE:
            self._list_capture.append(single_cell)

        cell = single_cell if type == Cells.EnumMove.M_SIMPLE else capture_cell                                
        self._current_move.append(cell)

        next_node : Node = Node(cell, self._score_node(type), self._current_node)
        self._current_node.next_move.append(next_node)

        return next_node
