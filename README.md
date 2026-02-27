# Configuration

# "graphics" : graphical interface module
#   "pygame" with loop frame ideal for animated graphics 2D
#   "tkinter" with event loop ideal for static widget graphics 2D(GUI)
#   "pyOpenGL" with loop frame, uses OpenGL API for 3D graphics
#   "webapp" future extensions
#   "console" no graphics, only command line

# "mode" : type of execution mode
#   "play" checkers game between player 1 and player 2
#   "view" view checkers game from archive
#   "data" Unsupervised Learning (UL) data extraction

# "player1_name" : identification player 1
#   "<name_player> name player for storage data
 
# "player1_engine" : type of decision engine for player 1
#   N.B.: valid only in 'play' mode !
#   "player" mouse or keyboard moves
#   "classic" MiniMax + Alpha-Beta Pruning
#   "SL" Supervised Learning
#   "RL" Reinforcement Learning

# "player2_name" : identification player 2
#   "<name_player> name player for storage data
 
# "player2_engine" : type of decision engine for player 2
#   N.B.: valid only in 'play' mode !
#   "player" mouse or keyboard moves
#   "classic" MiniMax + Alpha-Beta Pruning
#   "supervised" Supervised Learning (SL)
#   "reinforcement" Reinforcement Learning (RL)

# "parity_move" : Maximum number of moves without capturing any pieces and
# without moving any pieces (counted by both players)

# "restore" : restore checkerboards state from archive /restores
#   N.B.: delete option if normal game start !
#   "<name_checkerboard> checkerboard state name

# "history_database" : activation of historical game storage on database
# 	N.B.: if omitted, storing does not occur !
#   "<name_database> database name for game to storage

# "import_pdn" : PDN name from which to view the game
#   N.B.: valid only in 'view' mode !
#   "<name_pdn> PDN name for import/view

# "pk_game" : game identifier to view
#   N.B.: valid only in 'view' mode !
#   "<pk_game> game identifier in the chosen database (primary key=datetime)
#   N.B.: se PDN il time determina il numero della partita con stessa data !

# "seed" : use for randomization with testable determinism

# N.B.: TODO UL type option (with archive /dataset) !
#   N.B.: valid only in 'data' mode !
