class MovesPlayer():
    """
    Class     

    movesPlayer
    movesPiece
    moveRules

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

    def __init__(self):
        """
        Constructor 

        @param -: .
        """

        #self.pieces = {}
