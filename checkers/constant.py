# tests
CHECK_TREE = False

# checkerboard size
DIM_CKECKERBOARD = 8

# maximum number of dark cells
MAX_DARK_CELLS = 32

# maximum number of man or king
MAX_MAN = 12
MAX_KING = MAX_MAN + MAX_MAN

# maximun numeber if moves for cell
MAX_CELL_MOVE = 4

# screen width x height
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# Cell dimension
CELL_WIDTH = SCREEN_WIDTH // DIM_CKECKERBOARD
CELL_HEIGHT = SCREEN_HEIGHT // DIM_CKECKERBOARD


"""
NOTE DOMANDE :

- # Question 001 
  sintassi BaseClass
  come inizializzare pygame da interfaccia in checkerboard

- una classe complessa come moves.py, è meglio usarla come oggetto locale
in una funzione al momento di dover muovere, o dichiararla all'avvio della
applicazione per avere meno overhead ?

- tecnica per copiare deque in tupla senza distruggerla ?
- le tuple possono essere confrontate (primo elemento piu significativo) ?

- con pygame/tkinter posso visualizzare dei messaggi ?

"""

