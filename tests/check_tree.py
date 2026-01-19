from typing import Optional
from checkers.engine.game.move import Node
from checkers.constant import MAX_CELL_MOVE

class CheckTree:

    def __init__(self):
        self.read_move : list[int] = []
        self.root : Optional[Node] = None
        self.set_move : set = {}

    def test_tree(self, root: Node, set_move: set[tuple[int, ...]]):
        if root != None:
            self.root = root
            self.set_move = set_move
            self._read_node(root)

    # recorsive read of tree
    def _read_node(self, node: Node):
        if len(node.next_move) != MAX_CELL_MOVE:
            raise ValueError(f"Incomplete node.next_move !")

        if node != self.root:
            self.read_move.append(node.index_cell)

        not_child = True
        for child in node.next_move:
            if child != None:
                not_child = False
                self._read_node(child)

        if not_child:
            t = tuple(self.read_move)
            if t in self.set_move:
                self.set_move.discard(t)
            else:
                raise ValueError(f"Move not present in set !")

        self.read_move = self.read_move[:-1]
