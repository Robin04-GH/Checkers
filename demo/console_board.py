#from colorama import Fore, Back, Style, init
from rich.console import Console
from rich.table import Table
from rich.style import Style
from rich.text import Text

"""
def draw_board():
    board = [
        ['⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛'],
        ['⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛'],
        ['⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛'],
        ['⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛'],
    ]
    for row in board:
        print(" ".join(row))

def draw_colored_board():
    board = [
        [Back.BLACK + " " + Style.RESET_ALL, Back.WHITE + " " + Style.RESET_ALL] * 4,
        [Back.WHITE + " " + Style.RESET_ALL, Back.BLACK + " " + Style.RESET_ALL] * 4,
    ] * 4
    for row in board:
        print("".join(row))

def draw_board_with_unicode():
    board = [
        ['\u2B1B', '\u2B1C', '\u26AB', '\u2B1C'],
        ['\u2B1C', '\u26AA', '\u2B1C', '\u2B1B'],
        ['\u2B1B', '\u2B1C', '\u2B1B', '\u2B1C'],
        ['\u2B1C', '\u25A0', '\u2B1C', '\u25A1'],
    ]
    for row in board:
        print(" ".join(row))

# Inizializza Colorama
init(autoreset=True)
init(strip=False)  # Forza le sequenze ANSI

print(Fore.RED + "Questo dovrebbe essere rosso.")
print(Fore.BLUE + "Questo dovrebbe essere blu.")
print(Style.RESET_ALL + "Questo è normale.")

def draw_draughts_board():
    board = [
        # Pedine bianche, dame bianche in rosso
        ['⬛', Fore.RED + '⚪' + Style.RESET_ALL, '⬛', '⚪', '⬛', Fore.RED + '⚪' + Style.RESET_ALL, '⬛', '⚪'],
        # Pedine nere, dame nere in blu
        [Fore.BLUE + '⚫' + Style.RESET_ALL, '⬛', '⚫', '⬛', Fore.BLUE + '⚫' + Style.RESET_ALL, '⬛', '⚫', '⬛'],
        # Celle vuote
        ['⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛'],
        # Altre pedine o celle vuote
        ['⬛', '⚪', '⬛', Fore.RED + '⚪' + Style.RESET_ALL, '⬛', '⚪', '⬛', Fore.RED + '⚪' + Style.RESET_ALL],
        ['⬜', '⬛', Fore.BLUE + '⚫' + Style.RESET_ALL, '⬛', '⚫', '⬛', Fore.BLUE + '⚫' + Style.RESET_ALL, '⬛'],
        ['⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛', '⬜', '⬛', '⬜', '⬛']
    ]
    for row in board:
        print(" ".join(row))

def draw_draughts_board_back():
    board = [
        [Back.RED + ' ⚪ ' + Style.RESET_ALL, Back.BLACK + '⬛' + Style.RESET_ALL],
        [Back.BLUE + ' ⚫ ' + Style.RESET_ALL, Back.BLACK + '⬜' + Style.RESET_ALL],
        ['⬛', '⬜', '⬛', '⬜'],
        ['⬜', '⬛', '⬜', '⬛'],
    ]
    for row in board:
        print("".join(row))

# Inizializza la console di Rich
console = Console()

def draw_draughts_board_rich():
    # Crea una tabella per rappresentare la scacchiera
    board = Table(show_header=False, show_lines=False, padding=(0, 1), box=None)
    
    # Rappresentazione delle pedine e delle dame
    # ⚫: pedina nera, ⚪: pedina bianca
    # 🔴: dama nera, 🔵: dama bianca
    draughts_board = [
        ["⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪"],
        ["⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛"],
        ["⬛", "⚫", "⬛", "⚫", "⬛", "⚫", "⬛", "⚫"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜"],
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛"],
        ["🔴", "⬛", "⚫", "⬛", "⚫", "⬛", "⚫", "⬛"],
        ["⬛", "🔵", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪"],
        ["⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛"]
    ]
    
    # Aggiungi le righe della scacchiera alla tabella
    for row in draughts_board:
        board.add_row(*row)
    
    # Stampa la scacchiera
    console.print(board)
"""

# Inizializza la console di Rich
console = Console()

def draw_draughts_board_legend():
    # Crea una tabella per rappresentare la scacchiera
    board = Table(show_header=True, show_lines=False, padding=(0, 1), box=None)
    
    # Aggiungi gli header (colonne) numerici
    headers = [" "] + [str(i) for i in range(1, 9)]
    board.add_row(*headers)
    
    # Rappresentazione delle pedine e delle dame
    # ⚫: pedina nera, ⚪: pedina bianca
    # 🔴: dama nera, 🔵: dama bianca
    draughts_board = [
        ["⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "\U0001F7EB"],
        ["⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "\U0001F7E0"],
        ["⬛", "⚫", "⬛", "⚫", "⬛", "⚫", "⬛", "\U0001F7E4"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "\u2B1C"],
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", Text("⬤", style="bold black")],
        ["🔴", "⬜", "⚫", "⬛", "⚫", "⬛", "⚫", Text("🟡", style="bold yellow")],
        ["⬛", "🔵", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪"],
        ["⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛"]
    ]
    
    # Aggiungi le righe della scacchiera, con indici numerici per ogni riga
    for idx, row in enumerate(draughts_board, start=1):
        board.add_row(str(idx), *row)
    
    # Stampa la scacchiera
    console.print(board)

def draw_reverse_unicode():
    # Simboli normali
    normal_white = Style(color="white", bgcolor="black", bold=True)
    normal_black = Style(color="black", bgcolor="white", bold=True)
    
    # Reverse (invertito)
    reverse_white = Style(color="black", bgcolor="white", bold=True)
    reverse_black = Style(color="white", bgcolor="black", bold=True)

    # Stampa simboli normali e invertiti
    console.print("Simbolo Bianco (Normale): ⚪", style=normal_white)
    console.print("Simbolo Nero (Normale): ⚫", style=normal_black)
    console.print("Simbolo Bianco (Reverse): ⚪", style=reverse_white)
    console.print("Simbolo Nero (Reverse): ⚫", style=reverse_black)

def draw_draughts_board_with_reverse():
    # Crea una tabella per rappresentare la scacchiera
    board = Table(show_header=True, show_lines=False, padding=(0, 1), box=None)

    # Aggiungi gli header (colonne) numerici
    headers = [" "] + [str(i) for i in range(1, 9)]
    board.add_row(*headers)

    # Stile per celle bianche e nere con reverse
    white_cell = Style(color="black", bgcolor="white")
    black_cell = Style(color="white", bgcolor="black")

    # Pedine e dame
    normal_white_piece = Style(color="white", bold=True)
    normal_black_piece = Style(color="black", bold=True)
    king_white_piece = Style(color="blue", bold=True)
    king_black_piece = Style(color="red", bold=True)

    # Rappresentazione della scacchiera con pedine e dame
    draughts_board = [
        # Celle bianche e nere alternate con pedine
        ["⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪"],
        ["⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛"],
        ["⬛", "⚫", "⬛", "⚫", "⬛", "⚫", "⬛", "⚫"],
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜"],
        ["🔴", "⬛", "⚫", "⬛", "⚫", "⬛", "⚫", "⬛"],
        ["⬛", "🔵", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪"],
        ["⚪", "⬛", "⚪", "⬛", "⚪", "⬛", "⚪", "⬛"]
    ]

    # Costruisci la scacchiera con le celle e le pedine
    for idx, row in enumerate(draughts_board, start=1):
        formatted_row = []
        for col, cell in enumerate(row, start=1):
            # Determina lo stile della cella (bianco o nero alternato)
            if (idx + col) % 2 == 0:
                formatted_row.append(f"[{white_cell}]{cell}[/{white_cell}]")
            else:
                formatted_row.append(f"[{black_cell}]{cell}[/{black_cell}]")

    # Stampa la scacchiera
    console.print(board)

def draw_draughts_board_with_reverse2():
    # Crea una tabella per rappresentare la scacchiera
    board = Table(show_header=True, show_lines=False, padding=(0, 1), box=None)

    # Aggiungi gli header (colonne) numerici
    headers = [" "] + [str(i) for i in range(1, 9)]
    board.add_row(*headers)

    # Stile per celle bianche e nere con reverse
    white_cell = "[on black]⬜[/on black]"  # Sfondo nero con simbolo bianco
    black_cell = "[on white]⬛[/on white]"  # Sfondo bianco con simbolo nero

    # Pedine e dame
    white_piece = "[bold white]⚪[/bold white]"  # Pedina bianca
    black_piece = "[bold black]⚫[/bold black]"  # Pedina nera
    white_king = "[bold blue]🔵[/bold blue]"    # Dama bianca (blu)
    black_king = "[bold red]🔴[/bold red]"     # Dama nera (rossa)

    # Rappresentazione della scacchiera con pedine e dame
    draughts_board = [
        [black_cell, white_piece, black_cell, white_piece, black_cell, white_piece, black_cell, white_piece],
        [white_piece, black_cell, white_piece, black_cell, white_piece, black_cell, white_piece, black_cell],
        [black_cell, black_piece, black_cell, black_piece, black_cell, black_piece, black_cell, black_piece],
        [black_cell, white_cell, black_cell, white_cell, black_cell, white_cell, black_cell, white_cell],
        [white_cell, black_cell, white_cell, black_cell, white_cell, black_cell, white_cell, black_cell],
        [black_king, black_cell, black_piece, black_cell, black_piece, black_cell, black_piece, black_cell],
        [black_cell, white_king, black_cell, white_piece, black_cell, white_piece, black_cell, white_piece],
        [white_piece, black_cell, white_piece, black_cell, white_piece, black_cell, white_piece, black_cell],
    ]

    # Costruisci la scacchiera con indici numerici
    for idx, row in enumerate(draughts_board, start=1):
        board.add_row(str(idx), *row)

    # Stampa la scacchiera
    console.print(board)

def draw_draughts_board_custom():
    # Crea una tabella per rappresentare la scacchiera
    board = Table(show_header=True, show_lines=False, padding=(0, 1), box=None)

    # Aggiungi gli header (colonne) numerici
    headers = [" "] + [str(i) for i in range(1, 9)]
    board.add_row(*headers)

    # Simboli Unicode
    white_space = "[on black] [/on black]"  # Cella chiara con "reverse" (spazio bianco)
    black_cell = "⬛"                        # Cella scura senza reverse
    white_piece = "⚪"                       # Pedina bianca senza sfondo
    black_piece = "⚫"                       # Pedina nera senza sfondo

    # Rappresentazione della scacchiera con pedine
    draughts_board = [
        # Celle scure con pedine bianche
        [black_cell, white_space, black_cell, white_space, black_cell, white_space, black_cell, white_space],
        [white_space, black_cell, white_space, black_cell, white_space, black_cell, white_space, black_cell],
        [black_cell, black_piece, black_cell, black_piece, black_cell, black_piece, black_cell, black_piece],
        [black_cell, white_space, black_cell, white_space, black_cell, white_space, black_cell, white_space],
        [white_space, black_cell, white_space, black_cell, white_space, black_cell, white_space, black_cell],
        [black_piece, black_cell, black_piece, black_cell, black_piece, black_cell, black_piece, black_cell],
        [black_cell, white_piece, black_cell, white_piece, black_cell, white_piece, black_cell, white_piece],
        [white_piece, black_cell, white_piece, black_cell, white_piece, black_cell, white_piece, black_cell],
    ]

    # Aggiungi le righe della scacchiera con indici numerici
    for idx, row in enumerate(draughts_board, start=1):
        board.add_row(str(idx), *row)

    # Stampa la scacchiera
    console.print(board)

def get_move():
    start_cell = input("Inserisci l'ID della cella di partenza: ")
    end_cell = input("Inserisci l'ID della cella di destinazione: ")
    return start_cell, end_cell

# Esegui la funzione
# draw_draughts_board_custom()
# draw_draughts_board_with_reverse2()
# draw_draughts_board_with_reverse()
# draw_reverse_unicode()
draw_draughts_board_legend()
# draw_draughts_board_rich()

# draw_draughts_board_back()
# draw_draughts_board()
# draw_board_with_unicode()
# draw_colored_board()
# draw_board()
get_move()