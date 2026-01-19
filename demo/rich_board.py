from rich.console import Console
from rich.text import Text

def crea_quadrato(dimensione, colore_sfondo, simbolo_unicode, colore_simbolo):
    console = Console()
    
    # Genera il quadrato riga per riga
    quadrato = []
    for riga in range(dimensione):
        if riga == dimensione // 2:  # Riga centrale per il simbolo
            simbolo = Text(
                simbolo_unicode.center(dimensione),
                style=f"{colore_simbolo} on {colore_sfondo}",
            )
            quadrato.append(simbolo)
        else:
            riga_testo = " " * dimensione
            riga_colore = Text(riga_testo, style=f"on {colore_sfondo}")
            quadrato.append(riga_colore)
    
    # Stampa il quadrato con Rich
    for riga in quadrato:
        console.print(riga)

# Parametri
dimensione = 5  # Dimensione del quadrato
colore_sfondo = "blue"  # Colore di sfondo
simbolo_unicode = "★"  # Simbolo Unicode
colore_simbolo = "yellow"  # Colore del simbolo

crea_quadrato(dimensione, colore_sfondo, simbolo_unicode, colore_simbolo)

