from typing import Optional
from checkers.engine.game.move import Node, Move
from checkers.constant import MAX_CELL_MOVE

class CheckTree:
    """
    Class for testing the tree of moves
    """

    def __init__(self):
        self.origin : int = 0
        self.read_destinations : list[int] = []
        self.read_captures : list[int] = []
        self.root : Optional[Node] = None
        self.set_move : set[Move] = {}

    def test_tree(self, root: Node, set_move: set[Move]):
        if root != None:
            self.root = root
            self.set_move = set_move
            self._read_node(root)

    # recorsive read of tree
    def _read_node(self, node: Node):
        if len(node.next_move) != MAX_CELL_MOVE:
            raise ValueError(f"Incomplete node.next_move !")

        if node != self.root:
            self.read_destinations.append(node.index_cell)
            if node.score.last_capture_cell >= 0:
                self.read_captures.append(node.score.last_capture_cell)
        else:
            self.origin = node.index_cell

        not_child = True
        for child in node.next_move:
            if child != None:
                not_child = False
                self._read_node(child)

        if not_child:
            _move = Move(self.origin, tuple(self.read_destinations), tuple(self.read_captures))
            if _move in self.set_move:
                self.set_move.discard(_move)
            else:
                raise ValueError(f"Move not present in set !")

        self.read_destinations = self.read_destinations[:-1]
        if len(self.read_captures) > 0:
            self.read_captures = self.read_captures[:-1]
