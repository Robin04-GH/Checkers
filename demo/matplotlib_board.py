"""
import matplotlib.pyplot as plt

# creazione della griglia della lamiera
fig, ax = plt.subplots(figsize=(8,8))
ax.set_xlim([0,8])
ax.set_ylim([0,8])

# disegno delle caselle della damiera
for i in range(8):
    for j in range(8):
        if (i+j)%2 == 0:
            ax.add_patch(plt.Rectangle((i,j), 1, 1, fill=True, color='black'))
        else:
            ax.add_patch(plt.Rectangle((i,j), 1, 1, fill=True, color='white'))

# Posizionamanto delle pedine e delle dame
pedine_bianche = [(i, j) for i in range(3) for j in range(8) if (i + j % 2) != 0]
pedine_nere = [(i, j) for i in range(5, 8) for j in range(8) if (i + j % 2) != 0]

for posizione in pedine_bianche:
    ax.add_patch(plt.Circle(posizione, 0.3, color='white'))
for posizione in pedine_nere:
    ax.add_patch(plt.Circle(posizione, 0.3, color='black'))

plt.title('Disposizione iniziale della dama')
plt.show()
"""

# Note :
# - Heatmap (libreria Matplotlib) : plt.imcolor(M[i][j].color) !
# - Usare anche la funzione 'scatter' per la posizione dei pezzi !

"""
# Disegnare simboli Unicode su terminale 
import matplotlib.pyplot as plt

testo = "Python <simbolo> è fantastico !"

# Crea un grafico di testo
plt.text(0.5, 0.5, testo, ha='center', va='center', fontsize=20)
plt.axis('off')     # Nasconde gli assi
plt.show()
"""

# N.B.: la visualizzazione corretta dei simboli Unicode dipende dal supporto
# del terminale e della configurazione del sistema. Se si utilizza IDLE, potrebbe
# essere necessario gestire specifici problemi di codifica (vedere forum Python) !2

"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_draughts_board_with_pieces():
    # Dimensione della scacchiera
    board_size = 8

    # Crea una figura e un'area di disegno
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, board_size)
    ax.set_ylim(0, board_size)
    ax.set_aspect('equal')

    # Colori delle celle
    light_gray = '#D3D3D3'  # Grigio chiaro
    dark_gray = '#A9A9A9'   # Grigio scuro

    # Disegna le celle della scacchiera
    for row in range(board_size):
        for col in range(board_size):
            if (row + col) % 2 == 0:
                # Celle scure
                ax.add_patch(patches.Rectangle((col, row), 1, 1, color=dark_gray))
            else:
                # Celle chiare
                ax.add_patch(patches.Rectangle((col, row), 1, 1, color=light_gray))

    # Posiziona le pedine e le dame esclusivamente sulle celle scure
    pieces = [
        # Pedine bianche (solo su celle nere)
        (1, 0, '⚪'), (3, 0, '⚪'), (5, 0, '⚪'), (7, 0, '⚪'),
        (0, 1, '⚪'), (2, 1, '⚪'), (4, 1, '⚪'), (6, 1, '⚪'),

        # Pedine nere (solo su celle nere)
        (0, 6, '⚫'), (2, 6, '⚫'), (4, 6, '⚫'), (6, 6, '⚫'),
        (1, 7, '⚫'), (3, 7, '⚫'), (5, 7, '⚫'), (7, 7, '⚫'),

        # Dame bianche
        (3, 2, '🔵'),
        
        # Dame nere
        (4, 5, '🔴')
    ]

    for x, y, symbol in pieces:
        # Colore del testo basato sul simbolo
        color = 'white' if symbol in ['⚪', '🔵'] else 'red' if symbol == '🔴' else 'black'
        ax.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=20, color=color)

    # Rimuovi assi
    ax.axis('off')

    # Mostra la scacchiera
    plt.show()

# Esegui la funzione per disegnare la scacchiera
draw_draughts_board_with_pieces()
"""

"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_draughts_board_with_custom_dames():
    # Dimensione della scacchiera
    board_size = 8

    # Crea una figura e un'area di disegno
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, board_size)
    ax.set_ylim(0, board_size)
    ax.set_aspect('equal')

    # Colori delle celle
    light_gray = '#D3D3D3'  # Grigio chiaro
    dark_gray = '#A9A9A9'   # Grigio scuro

    # Disegna le celle della scacchiera
    for row in range(board_size):
        for col in range(board_size):
            if (row + col) % 2 == 0:
                # Celle scure: grigio scuro
                ax.add_patch(patches.Rectangle((col, row), 1, 1, color=dark_gray))
            else:
                # Celle chiare: grigio chiaro
                ax.add_patch(patches.Rectangle((col, row), 1, 1, color=light_gray))

    # Posiziona le pedine e le dame esclusivamente sulle celle scure
    pieces = [
        # Pedine bianche (solo su celle scure)
        (1, 0, '⚪'), (3, 0, '⚪'), (5, 0, '⚪'), (7, 0, '⚪'),
        (0, 1, '⚪'), (2, 1, '⚪'), (4, 1, '⚪'), (6, 1, '⚪'),

        # Pedine nere (solo su celle scure)
        (0, 6, '⚫'), (2, 6, '⚫'), (4, 6, '⚫'), (6, 6, '⚫'),
        (1, 7, '⚫'), (3, 7, '⚫'), (5, 7, '⚫'), (7, 7, '⚫'),

        # Dame bianche (cerchi blu)
        (3, 2, 'dame_white'),
        
        # Dame nere (cerchi rossi)
        (4, 5, 'dame_black')
    ]

    for x, y, symbol in pieces:
        if symbol == '⚪':  # Pedina bianca
            ax.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=20, color='white')
        elif symbol == '⚫':  # Pedina nera
            ax.text(x + 0.5, y + 0.5, symbol, ha='center', va='center', fontsize=20, color='black')
        elif symbol == 'dame_white':  # Dama bianca (cerchio blu)
            ax.add_patch(patches.Circle((x + 0.5, y + 0.5), 0.3, color='blue'))
        elif symbol == 'dame_black':  # Dama nera (cerchio rosso)
            ax.add_patch(patches.Circle((x + 0.5, y + 0.5), 0.3, color='red'))

    # Rimuovi assi
    ax.axis('off')

    # Mostra la scacchiera
    plt.show()

# Esegui la funzione per disegnare la scacchiera
draw_draughts_board_with_custom_dames()
"""

"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_custom_draughts_board():
    # Dimensione della scacchiera
    board_size = 8

    # Crea una figura e un'area di disegno
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, board_size)
    ax.set_ylim(0, board_size)
    ax.set_aspect('equal')

    # Colori delle celle
    light_gray = '#D3D3D3'  # Grigio chiaro
    dark_gray = '#A9A9A9'   # Grigio scuro

    # Disegna le celle della scacchiera
    for row in range(board_size):
        for col in range(board_size):
            if (row + col) % 2 == 0:
                # Celle scure: grigio scuro
                ax.add_patch(patches.Rectangle((col, board_size - row - 1), 1, 1, color=dark_gray))
            else:
                # Celle chiare: grigio chiaro
                ax.add_patch(patches.Rectangle((col, board_size - row - 1), 1, 1, color=light_gray))

    # Posiziona i pezzi esclusivamente sulle celle scure
    pieces = [
        # Pedine bianche (solo su celle scure)
        (1, 0, 'white_piece'), (3, 0, 'white_piece'), (5, 0, 'white_piece'), (7, 0, 'white_piece'),
        (0, 1, 'white_piece'), (2, 1, 'white_piece'), (4, 1, 'white_piece'), (6, 1, 'white_piece'),

        # Pedine nere (solo su celle scure)
        (0, 6, 'black_piece'), (2, 6, 'black_piece'), (4, 6, 'black_piece'), (6, 6, 'black_piece'),
        (1, 7, 'black_piece'), (3, 7, 'black_piece'), (5, 7, 'black_piece'), (7, 7, 'black_piece'),

        # Dame bianche
        (3, 2, 'white_dame'),

        # Dame nere
        (4, 5, 'black_dame')
    ]

    for x, y, symbol in pieces:
        if symbol == 'white_piece':  # Pedina bianca (cerchio pieno bianco)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, color='white'))
        elif symbol == 'black_piece':  # Pedina nera (cerchio pieno nero)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, color='black'))
        elif symbol == 'white_dame':  # Dama bianca (doppio cerchio blu)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, edgecolor='blue', facecolor='none', linewidth=2))
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.2, color='blue'))
        elif symbol == 'black_dame':  # Dama nera (doppio cerchio rosso)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, edgecolor='red', facecolor='none', linewidth=2))
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.2, color='red'))

    # Rimuovi assi
    ax.axis('off')

    # Mostra la scacchiera
    plt.show()

# Esegui la funzione per disegnare la scacchiera
draw_custom_draughts_board()
"""


import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_board(pieces):
    # Dimensione della scacchiera
    board_size = 8

    # Crea una figura e un'area di disegno
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, board_size)
    ax.set_ylim(0, board_size)
    ax.set_aspect('equal')

    # Colori delle celle
    light_gray = '#D3D3D3'  # Grigio chiaro
    dark_gray = '#A9A9A9'   # Grigio scuro

    # Disegna le celle della scacchiera
    for row in range(board_size):
        for col in range(board_size):
            if (row + col) % 2 == 0:
                # Celle scure: grigio scuro
                ax.add_patch(patches.Rectangle((col, board_size - row - 1), 1, 1, color=dark_gray))
            else:
                # Celle chiare: grigio chiaro
                ax.add_patch(patches.Rectangle((col, board_size - row - 1), 1, 1, color=light_gray))

    # Disegna i pezzi sulla scacchiera
    for x, y, symbol in pieces:
        if symbol == 'white_piece':  # Pedina bianca (cerchio pieno bianco)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, color='white'))
        elif symbol == 'black_piece':  # Pedina nera (cerchio pieno nero)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, color='black'))
        elif symbol == 'white_dame':  # Dama bianca (doppio cerchio blu)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, edgecolor='blue', facecolor='none', linewidth=2))
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.2, color='blue'))
        elif symbol == 'black_dame':  # Dama nera (doppio cerchio rosso)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, edgecolor='red', facecolor='none', linewidth=2))
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.2, color='red'))

    # Rimuovi assi
    ax.axis('off')

    # Mostra la scacchiera
    plt.show()


def get_player_move():
    print("Inserisci la tua mossa (esempio: da 6,3 a 5,4):")
    start = input("Cella di partenza (riga,colonna): ")
    end = input("Cella di arrivo (riga,colonna): ")
    
    # Converti l'input in coordinate numeriche
    start_row, start_col = map(int, start.split(","))
    end_row, end_col = map(int, end.split(","))
    
    return (start_row, start_col), (end_row, end_col)


def is_valid_move(start, end, pieces):
    # Controlla che la posizione di partenza abbia un pezzo
    for piece in pieces:
        if piece[0] == start[1] and piece[1] == start[0]:
            # Controlla che la posizione finale sia una cella scura
            if (end[0] + end[1]) % 2 == 0:
                return True, piece
    return False, None


def move_piece(start, end, pieces, moving_piece):
    # Rimuovi il pezzo dalla posizione di partenza e aggiungilo a quella di arrivo
    pieces.remove(moving_piece)
    pieces.append((end[1], end[0], moving_piece[2]))


def main():
    # Posizioni iniziali dei pezzi
    pieces = [
        # Pedine bianche
        (1, 0, 'white_piece'), (3, 0, 'white_piece'), (5, 0, 'white_piece'), (7, 0, 'white_piece'),
        (0, 1, 'white_piece'), (2, 1, 'white_piece'), (4, 1, 'white_piece'), (6, 1, 'white_piece'),

        # Pedine nere
        (0, 6, 'black_piece'), (2, 6, 'black_piece'), (4, 6, 'black_piece'), (6, 6, 'black_piece'),
        (1, 7, 'black_piece'), (3, 7, 'black_piece'), (5, 7, 'black_piece'), (7, 7, 'black_piece'),

        # Dame bianche
        (3, 2, 'white_dame'),

        # Dame nere
        (4, 5, 'black_dame')
    ]

    # Disegna la scacchiera iniziale
    draw_board(pieces)

    # Ciclo principale del gioco
    while True:
        start, end = get_player_move()
        valid, moving_piece = is_valid_move(start, end, pieces)
        if valid:
            move_piece(start, end, pieces, moving_piece)
            draw_board(pieces)
        else:
            print("Mossa non valida! Riprova.")

# Avvia il gioco
if __name__ == '__main__':
    main()


"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Variabili globali
pieces = [
    # Pedine bianche
    (1, 0, 'white_piece'), (3, 0, 'white_piece'), (5, 0, 'white_piece'), (7, 0, 'white_piece'),
    (0, 1, 'white_piece'), (2, 1, 'white_piece'), (4, 1, 'white_piece'), (6, 1, 'white_piece'),

    # Pedine nere
    (0, 6, 'black_piece'), (2, 6, 'black_piece'), (4, 6, 'black_piece'), (6, 6, 'black_piece'),
    (1, 7, 'black_piece'), (3, 7, 'black_piece'), (5, 7, 'black_piece'), (7, 7, 'black_piece'),

    # Dame bianche
    (3, 2, 'white_dame'),

    # Dame nere
    (4, 5, 'black_dame')
]
selected_piece = None  # Salva il pezzo selezionato


def draw_board(ax, pieces):
    # Dimensione della scacchiera
    board_size = 8

    # Colori delle celle
    light_gray = '#D3D3D3'  # Grigio chiaro
    dark_gray = '#A9A9A9'   # Grigio scuro

    # Ripulisci l'area di disegno
    ax.clear()

    # Disegna le celle della scacchiera
    for row in range(board_size):
        for col in range(board_size):
            if (row + col) % 2 == 0:
                ax.add_patch(patches.Rectangle((col, board_size - row - 1), 1, 1, color=dark_gray))
            else:
                ax.add_patch(patches.Rectangle((col, board_size - row - 1), 1, 1, color=light_gray))

    # Disegna i pezzi sulla scacchiera
    for x, y, symbol in pieces:
        if symbol == 'white_piece':  # Pedina bianca
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, color='white'))
        elif symbol == 'black_piece':  # Pedina nera
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, color='black'))
        elif symbol == 'white_dame':  # Dama bianca (doppio cerchio blu)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, edgecolor='blue', facecolor='none', linewidth=2))
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.2, color='blue'))
        elif symbol == 'black_dame':  # Dama nera (doppio cerchio rosso)
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.3, edgecolor='red', facecolor='none', linewidth=2))
            ax.add_patch(patches.Circle((x + 0.5, board_size - y - 0.5), 0.2, color='red'))

    # Rimuovi assi
    ax.axis('off')


def on_click(event):
    global selected_piece, pieces

    # Calcola la cella cliccata
    col = int(event.xdata)
    row = 7 - int(event.ydata)

    if selected_piece is None:
        # Seleziona il pezzo nella cella cliccata
        for piece in pieces:
            if piece[0] == col and piece[1] == row:
                selected_piece = piece
                print(f"Pezzo selezionato: {selected_piece}")
                return
    else:
        # Muovi il pezzo alla nuova posizione
        print(f"Mossa verso: ({row}, {col})")
        pieces.remove(selected_piece)
        pieces.append((col, row, selected_piece[2]))
        selected_piece = None

        # Aggiorna la scacchiera
        draw_board(ax, pieces)
        fig.canvas.draw()


# Configura la finestra di matplotlib
fig, ax = plt.subplots(figsize=(8, 8))
draw_board(ax, pieces)

# Collega l'evento di click
fig.canvas.mpl_connect('button_press_event', on_click)

# Mostra la scacchiera
plt.show()
"""

"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Variabili globali
pieces = [
    (1, 0, 'white_piece'), (3, 0, 'white_piece'), (5, 0, 'white_piece'), (7, 0, 'white_piece'),
    (0, 1, 'white_piece'), (2, 1, 'white_piece'), (4, 1, 'white_piece'), (6, 1, 'white_piece'),
    (0, 6, 'black_piece'), (2, 6, 'black_piece'), (4, 6, 'black_piece'), (6, 6, 'black_piece')
]
selected_piece = None

def draw_board(ax, pieces):
    #Disegna la scacchiera e i pezzi
    ax.clear()
    for row in range(8):
        for col in range(8):
            color = '#A9A9A9' if (row + col) % 2 == 0 else '#D3D3D3'
            ax.add_patch(patches.Rectangle((col, 7 - row), 1, 1, color=color))
    for x, y, symbol in pieces:
        if symbol == 'white_piece':
            ax.add_patch(patches.Circle((x + 0.5, 7 - y + 0.5), 0.3, color='white'))
        elif symbol == 'black_piece':
            ax.add_patch(patches.Circle((x + 0.5, 7 - y + 0.5), 0.3, color='black'))
    ax.axis('off')

def on_click(event):
    #Gestisce il clic del mouse
    global selected_piece
    if event.xdata is not None and event.ydata is not None:
        col = int(event.xdata)
        row = 7 - int(event.ydata)
        
        # Verifica se il clic è dentro la scacchiera
        if 0 <= col < 8 and 0 <= row < 8:
            print(f"Cliccato su cella: ({row}, {col})")
            if selected_piece is None:
                # Seleziona il pezzo se presente
                for piece in pieces:
                    if piece[0] == col and piece[1] == row:
                        selected_piece = piece
                        print(f"Pezzo selezionato: {selected_piece}")
            else:
                # Muovi il pezzo alla nuova posizione
                print(f"Spostato verso: ({row}, {col})")
                pieces.remove(selected_piece)
                pieces.append((col, row, selected_piece[2]))
                selected_piece = None
                draw_board(ax, pieces)
                fig.canvas.draw()
        else:
            print("Clic fuori dalla scacchiera!")

# Configura la finestra di matplotlib
fig, ax = plt.subplots(figsize=(8, 8))
draw_board(ax, pieces)

# Collega l'evento di click
fig.canvas.mpl_connect('button_press_event', on_click)

# Mostra la scacchiera
plt.show()
"""