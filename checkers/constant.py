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

# cell dimension
CELL_WIDTH = SCREEN_WIDTH // DIM_CKECKERBOARD
CELL_HEIGHT = SCREEN_HEIGHT // DIM_CKECKERBOARD

# timer blending (msec)
TIMER_PRESCALER = 20
BLENDING_DURATION = 250

# path
PATH_RESTORES = "restores/"
PATH_PDN = "pdn/"

# maximum number of characters per line
MAX_LINE_CHAR = 99999