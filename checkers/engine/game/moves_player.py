from typing import Optional
from checkers.constant import MAX_CELL_MOVE
from checkers.types import DestCellsType
from checkers.engine.game.state import State
from checkers.engine.game.move_rules import MoveRules
from checkers.engine.game.move import Score, Node, Move, EnumMove
from checkers.engine.game.cells import Cells

from checkers.constant import CHECK_TREE
if CHECK_TREE:
  from tests.check_tree import CheckTree

class MovesPlayer(MoveRules):
    """
    Class     

    - movesPlayer 
       classe che nel thread (o process) engine scansiona tutti i pezzi del player_turn per costruire il dict 
       di tutte le possibili mosse (score locale dict)
       N.B.: nella classe Pieces (reference dalla classe State) serve una funzione generatrice di pezzi del player !
    - moveRules
       classe chiamata da movesPlayer per costruire l'albero delle mosse data la cella di origine
    - 

    *** Dati :
    'move' = tupla di cell ID simple/capture (origine implicita)
       costruzione mosse attraverso deque tra tutte le possibili 
       combinazioni di celle permesse dalle regole del gioco.       
    'set' di 'move' con stessa origine
       collezione non ordinata delle 'move' (convertite in tuple)
       elementi unici ed immutabili.
       Selezionata una cella, il set contiene tutte le possibili mosse
       N.B.: non necessariamente tutto l'albero, dipende dagli score !
    'dict' di 'set' con chiave l'ID cella di origine del 'set'
       ogni set del 'dict' ha nella chiave le celle che possono 
       essere selezionate per effettuare la mossa
    N.B.: 'move', 'set' e 'dict' hanno il proprio livello di score !

    *** Logica per ricavare i dati :
    * per una data cella di origine 
      1) singolo step mossa in base alle regole del gioco 
      con incremento score
        - distinzione se pedina/dama e players per selezione delle
        diagionali (2 decrescenti(light)/crescenti(dark) o 4 se dama)
        - selezione direzione diagonale. La scansione delle al massimo 
        4+4 diagonali da valutare per la cella avvengono in ordine dal 
        quadrante 1 al 4 (stesso ordine degli elementi della tupla cells)
        - obbligo della cattura (prioritaria mossa capture su simple) :
          - leggo pezzo su capture
          - leggo pezzo su simple
          - capture possibile se simple occupata da avversario con 
          pezzo di qualità non superiore, con cella capture vuota
            N.B.: le pedine NON possono mangiare le dame !
            N.B.: nella lettura del pezzo presente su una cella,
          la cella di origine deve essere considerata libera
          perchè durante la mossa la pedina verrà spostata. 
          Inoltre non posso ripercorrere gli stessi rami della mossa in 
          costruzione perche le eventuali pedine avversarie sono già 
          state eliminate.       
          - se capture non possibile, valuto se simple vuota per 
          mossa semplice
            N.B.: gestione ottimizzazione comparando score incrementale
          con quello globale del set. Tuttavia se il passo è con 
          cattura dovrò comunque arrivare a completare la mossa per 
          valutare lo score. Invece se è una mossa semplice ed avevo 
          gia nel 'set' altri score maggiori, posso scartarla continuando
          la backtrace (albero virtuale sulle celle) !
            N.B.: una pedina può mangiare al massimo 3 pedine !
          - aggiornare con append() seconda deque pezzi già catturati
          - per ogni passo avviene la append() sulla deque 'move' 
          con incremento variabili di score se cattura :
           1) incremento pezzo catturato (pedina o dama)
           2) incremento dama catturata
           3) incremento indice step finchè >= 0, poi se è stata 
           catturata una dama inverto il segno per bloccarla
          - per ogni passo incrementare anche un conteggio globale
          dei passi relativi alla mossa (utile per backtracing dell'
          elemento 3 dello score)
          
        - per score si intendono 3 variabili che determinano l'obbligo
        di alcune mosse rispetto ad altre, in ordine di priorità sono :
          1) maggior numero di pezzi catturati
          2) maggior numero di dame catturate
          3) maggior indice (< 0) del passo che cattura la prima dama 
            N.B.: obbligo maggior qualità dei pezzi catturati o dove li
          incontra prima !    
            N.B.: ci sono 3 livelli di score :
          1) score incrementale a livello di singola mossa (deque)
          2) score globale a livello di 'set' (singolo pezzo, origine)
          3) score globale a livello di 'dict' (tutti i pezzi)

      2) ripetizione step mossa fino al suo completamento
      3) valutazione score ed eventuale aggiornamento 'set' di mosse
        - copiare l'intera deque come tupla nel set. 
        Valutare tecnica : prelevo elementi a sinistra (popleft) e 
        li appendo sulla tupla mentre rigenero una nuova deque con 
        append().
        - aggiorno lo score della mossa copiata, sullo score globale 
        del 'set' (per confronto)
      4) backtracing per successiva mossa :
        - salvo id ultima cella nella deque che servirà per assegnare
        l'indice del prossimo quadrante delle possibili diagonali
        - popright() sulla deque (eliminato elemento alla fine a destra)
        - valuto indice quadrante e se presenti altri rami proseguo
        il loop col prossimi step.
        - decremento degli elementi dello score e del conteggio passi
        - aggiornare deque pezzi già catturati con popright()
      5) completato l'albero virtuale di mosse aggiornamento del 'dict',
      confrontando  lo score del 'set' con quello globale del 'dict'.

    * ripetizione per tutte le celle del player con turno di mossa
      1) aggiornamento 'dict' di 'set', controllando lo score. 
      A parità di score con cattura, valutare la cella di origine,
      è obbligo muovere una dama rispetto ad una pedina.

    * fine partita :
    - la partita viene 'persa' quando un giocatore non ha piu mosse 
    possibili perchè i pezzi sono bloccati o tutti catturati.
    - viene considerata 'patta' quando dopo 50 mosse non sono stati piu
    catturati pezzi, col conteggio che si riazzera dopo ogni mossa 
    di una pedina.

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
                    # A parità di score devo catturare con la cella originale piu forte
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
            del root  # Inutile : elimina solo la variabile locale root !
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

    # Ritorna una tupla (_dest_cells) con gli indici di tutte le celle destinazione compresa quella precedente,
    # individuabile dall'indice sulla tupla (_previous_index)
    def get_destination_cells(self)->tuple[DestCellsType, int]:        
        _previous_index : int = -1
        _previous_cell : int = -1
        if self._actual_node.prev_move != None:
            _previous_cell = self._actual_node.prev_move.index_cell
            _cells : DestCellsType = Cells.get_moves(self._actual_node.index_cell, self._actual_node.score.type_move)
            try:
                _previous_index = _cells.index(_previous_cell)
            except ValueError:
                raise ValueError(f"Class MovesPlayer, get_destination_cells(): errore precedente mancante !")

        _dest_cells : list[int] = []
        if len(self._actual_node.next_move) != MAX_CELL_MOVE:
            raise ValueError(f"Class MovesPlayer, get_destination_cells() : dimensione next_move diversa da MAX_CELL_MOVE !")
        for _index, _node in enumerate(self._actual_node.next_move):
            _cell = _node.index_cell if _node != None else -1
            _dest_cells.append(_cell) if _index != _previous_index else _dest_cells.append(_previous_cell)

        return (tuple(_dest_cells), _previous_index)
    
    def upgrade_move(self, index:int):
        if index != -1:
            # Avanzamento
            next_node : Optional[Node] = self._actual_node.next_move[index]
            if next_node == None:
                raise ValueError(f"Class MovesPlayer, upgrade_move() : avanzamento mossa senza nodo !")
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
            # Annullamento
            prev_node : Optional[Node] = self._actual_node.prev_move
            if prev_node == None:
                raise ValueError(f"Class MovesPlayer, upgrade_move() : annullamento mossa senza nodo")
            self._actual_node = prev_node
            
            if self._actual_node.prev_move == None:
                self._actual_move = None
            else:
                self._actual_move = self._actual_move.remove_last()
    
    def finalize_move(self, move:Move)->bool:
        print(f"Move = {move}")
        if self._actual_move != move:
            raise ValueError(f"Class MovesPlayer, finalize_move() : mossa non sincronizzata !")        
        
        # Aggiornamento stato
        is_promoted_king : bool = self.state.update(move)
        self.reset_move()
        return is_promoted_king
