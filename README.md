# Configuration

# "graphics" : graphical interface module
#   "pygame" with loop frame ideal for animated graphics 2D
#   "tkinter" with event loop ideal for static widget graphics 2D(GUI)
#   "pyOpenGL" with loop frame, uses OpenGL API for 3D graphics
#   "webapp" future extensions

# "mode" : type of execution mode
#   "play" checkers game between player 1 and player 2
#   "view" view checkers game from archive
#   "data" Unsupervised Learning (UL) data extraction

# "player1" : type of decision engine for player 1
#   N.B.: valid only in 'play' mode !
#   "manual" mouse or keyboard moves
#   "classic" MiniMax + Alpha-Beta Pruning
#   "SL" Supervised Learning
#   "RL" Reinforcement Learning

# "player2" : type of decision engine for player 2
#   N.B.: valid only in 'play' mode !
#   "manual" mouse or keyboard moves
#   "classic" MiniMax + Alpha-Beta Pruning
#   "supervised" Supervised Learning (SL)
#   "reinforcement" Reinforcement Learning (RL)

# "restore" : restore checkerboards state from archive /restores
#   N.B.: delete option if normal game start !
#   "<name_checkerboard> checkerboard state name

# "history_database" : activation of historical game storage on database
# 	N.B.: if omitted, storing does not occur !
#   "<name_database> database name for game to storage

# "view_database" : database name from which to view the game
#   N.B.: valid only in 'view' mode !
#   "<name_database> database name from archive /database

# "view_id" : game identifier to view
#   N.B.: valid only in 'view' mode !
#   "<id> game identifier in the chosen database

# N.B.: TODO UL type option (with archive /dataset) !
#   N.B.: valid only in 'data' mode !

### Note ###

+ aggiungere opzione 'player1' e 'player2' per assegnare a ciascuno l'engine (manuale, autom. classico, autom. ML).

+ aggiungere opzione 'mode' per modalità operativa (play, view, data).

+ funzione reset scacchiera per posizionamento iniziale pedine (stato di inizio gioco) e sorteggio assegnamento colore ai player (visualizzazione lato scacchiera impostabile, leggi dopo ...). 

+ funzione per partire da uno stato scacchiera specifico, utile per test o riprendere partite sospese (con funzione di salvataggio stato e giocatore abilitato alla mossa su file JSON). Da config impostare nome del restore.

- la scacchiera a video puo essere liberamente ruotata di 180° essendo simmetrica per scambiare le pedine bianche o scure (della trasformazione tenerne conto quando si muovono le pedine)

- Aggiungere bar sotto il player in basso, e sopra al player in alto per visualizzare il player, il numero di mossa e in numero di pedine/dame.

- Aggiungere una label per messaggi sotto la scacchiera : 'Seleziona pedina, muove bianco/nero, fine partita, status engine, ...'.

- mosse col mouse : selezione pedina (tasto premuto), ricevo possibili celle delle mosse permesse (per cambiare mossa è necessario ritornare sulla cella iniziale), spostamento mouse con filtro e centri gravità (per evitare di vagare). Se lascio il mouse 
senza aver terminato la mossa, l'ultima cella spostata rimane selezionata. Occorre riprenderla col tasto premuto del mouse per completare la mossa o tornare indietro per altra scelta eventuale.
Se lascio il mouse quando era già su una cella di possibile destinazione, la mossa è effettuata e non è possibile tornare indietro.

- mosse con tastiera : selezione prima pedina automatica, usare frecce sx/dx per scelta selezione e per le 4 direzioni diagonali possibili usare i tasti T, U, N, V. Se ritorno nella cella iniziale riattivo anche le frecce per poter cambiare ancora pedina. La deselezione al termine percorso delle celle permesse avviene con invio (equivalente al rilascio del mouse) per confermare la mossa.

- gestione mosse : puo essere spostamento semplice o spostamento con cattura, anche multiplo. Prevedere stato avanzamento a dama.
Alcuni PDN riportano solo la cella iniziale e destinazione ma non quelle eventuali intermedie (indicando però come separatore numeri celle con 'x' per le catture anziche '-'). 
Se conversione PDN-database vengono esplicitate, se mosse manuali vengono eseguite per step (visualizzazione in tempo reale ogni step) infine con ML vengono ancora esplicitate (ma visualizzazione rimandata dopo la ricezione della mossa completa anche se animata a step).

+ la gestione 'view' permette di visionare le partite salvate sui database. Devono essere configurato il 'mode' come 'view' e sui token 'view_database' specificare il nome e 'view_id' la partita.
Per avanzare di una mossa click tasto sinistro sulla bar in basso o in alto dei player indistintamente, tenendo premuto per avanzamento continuo. Se tasto destro torna alla mossa precedente, se mantenuto continua il playback. 
Con i tasti usare le frecce avanti o indietro per singola mossa. Mantenute per continuo avanti o indietro.
Lo scorrimento mosse è ciclico e visibile nelle bar dei player.

- Convertitore PDN su database. Esplicitare sul database le celle dei salti intermedi sulle catture multiple se non indicati nel PDN.

+ funzione per storicizzare le partite salvando le mosse su database. Nel config aggiungere token 'histoty_database'.

- Schema sequenza gioco : 
  0) configurazione partita e sorteggio colore
  1) stato scacchiera (matrice posizione pedine/dame) con stato player abilitato alla mossa (il primo è quello di reset o inizio gioco, oppure quello iniziale configurato)
  2) gestione mossa player abilitato
  3) storicizzazione nuovo stato se attivata
  4) test fine partita
  5) cambio player abilitato alla mossa e loop su 2

- Struttura progetto :
  1) checkers.py per __main__, config e inizializzazioni classi base.
  2) in /game checkerboard.py per memoria scacchiera, inizializzazione (reset) o lettura stato iniziale e invio dati pedine per grafica.
  3) script per regole (possibili mosse) e loop sequenza gioco.
  4) in /graph script per grafica con varie tecniche (da config), e gestioni per mouse/tastiera (diverse in base al package usato).
  5) script per interfaccia comune tra diverse tecniche grafiche configurabili e modulo board.py (per dati scacchiera).
  6) in /engine/classic scelta mosse con tecniche deterministiche
  7) in /engine/ai script per ML (inferenza mossa ottimale)
  8) gestione database per dataset training/test o storico
