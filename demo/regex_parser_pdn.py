import re
from collections import defaultdict

# Patch 2 : ristrutturato parse_moves() per gestione corretta del risultato 
MOVE_RE = re.compile(r'^\d{1,2}(?:[-x]\d{1,2})+$')
TURN_RE = re.compile(r'^\d+\.$')
RESULT_RE = re.compile(r'^(1-0|0-1|1/2-1/2)$')

def parse_moves(moves_text):

    # Rimozione commenti
    moves_text = re.sub(r'\{[^}]*\}', '', moves_text)
    moves_text = re.sub(r'\[#.*?\]', '', moves_text)

    # Normalizzazione whitespace
    moves_text = re.sub(r'\s+', ' ', moves_text).strip()

    tokens = moves_text.split()

    # --- Estrazione risultato finale ---
    result = None
    if tokens and RESULT_RE.match(tokens[-1]):
        result = tokens.pop()   # rimuove il risultato dai token

    moves = []
    i = 0

    while i < len(tokens):

        token = tokens[i]

        if TURN_RE.match(token):

            turn_number = int(token[:-1])

            turn = {
                "move_number": turn_number,
                "white": None,
                "black": None
            }

            # White
            if i + 1 < len(tokens) and MOVE_RE.match(tokens[i + 1]):
                turn["white"] = tokens[i + 1]
                i += 2
            else:
                raise ValueError(f"Mossa white mancante al turno {turn_number}")

            # Black (opzionale)
            if i < len(tokens):
                if MOVE_RE.match(tokens[i]):
                    turn["black"] = tokens[i]
                    i += 1
                elif RESULT_RE.match(tokens[i]):
                    # sicurezza ulteriore (ridondanza)
                    result = tokens[i]
                    i += 1

            moves.append(turn)
            continue

        i += 1

    return moves, result

"""
MOVE_RE = re.compile(r'\d{1,2}(?:[-x]\d{1,2})+')
TURN_RE = re.compile(r'^\d+\.$')
RESULT_RE = re.compile(r'^(1-0|0-1|1/2-1/2)$')

def parse_moves(moves_text):
    # Rimozione commenti e marker
    moves_text = re.sub(r'\{[^}]*\}', '', moves_text)
    moves_text = re.sub(r'\[#.*?\]', '', moves_text)

    # Normalizza spazi
    moves_text = re.sub(r'\s+', ' ', moves_text).strip()

    tokens = moves_text.split()

    moves = []
    current_turn = None
    result = None

    i = 0
    while i < len(tokens):

        token = tokens[i]

        # Nuovo numero turno
        if TURN_RE.match(token):
            turn_number = int(token[:-1])
            current_turn = {
                "move_number": turn_number,
                "white": None,
                "black": None
            }

            # White move
            if i + 1 < len(tokens) and MOVE_RE.match(tokens[i + 1]):
                current_turn["white"] = tokens[i + 1]
                i += 2
            else:
                raise ValueError(f"White move mancante al turno {turn_number}")

            # Black move (opzionale)
            if i < len(tokens) and MOVE_RE.match(tokens[i]):
                current_turn["black"] = tokens[i]
                i += 1

            moves.append(current_turn)
            continue

        # Risultato partita
        if RESULT_RE.match(token):
            result = token
            break

        i += 1

    return moves, result
"""

import os
def parse_pdn(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split partite su [White "..."]
    games = re.split(r'(?=\[White\s+")', content.strip())

    parsed_games = []

    for game in games:

        if not game.strip():
            continue

        # ---- METADATA ----
        metadata = defaultdict(list)

        for key, value in re.findall(r'\[(\w+)\s+"([^"]*)"\]', game):
            metadata[key].append(value)

        # ---- MOSSE ----
        # Patch 1 : aggiunto parse_moves()
        moves_section = re.split(r'\n\s*\n', game, maxsplit=1)
        moves_text = moves_section[1] if len(moves_section) > 1 else ""
        moves, result = parse_moves(moves_text)

        """
        # Rimuove metadati iniziali
        moves_section = re.split(r'\n\s*\n', game, maxsplit=1)
        moves_text = moves_section[1] if len(moves_section) > 1 else ""

        # Rimuove commenti {}
        moves_text = re.sub(r'\{[^}]*\}', '', moves_text)

        # Rimuove marker tipo [#]
        moves_text = re.sub(r'\[#.*?\]', '', moves_text)

        moves_text = moves_text.strip()

        # Estrae mosse numerate
        move_pattern = re.compile(r'\d+\.\s*([^\.]+)')
        moves = [m.strip() for m in move_pattern.findall(moves_text)]
        """

        parsed_games.append({
            'metadata': dict(metadata),
            'moves': moves,
            'result': result
        })

    return parsed_games

# Esempio di utilizzo
file_path = 'pdn/CI2008.pdn'  # sostituisci con il percorso del tuo file

partite = parse_pdn(file_path)

for i, partita in enumerate(partite, 1):
    print(f"Partita {i}:")
    print("Metadati:", partita['metadata'])
    print("Mosse:", partita['moves'])
    print("Result:", partita['result'])
    print("-" * 40)

# Dopo patch 1:
# Questa è già una mini state-machine parser.
# Il prossimo step naturale è eliminare completamente le regex e 
# fare un vero tokenizer deterministico a caratteri, 
# più veloce e controllabile (specialmente su grandi dataset PDN).

# Dopo patch 2:
# Ora il tuo parser :
# - è deterministico
# - è strutturalmente corretto rispetto alla grammatica PDN
# - non confonde token strutturali con token semantici
# - separa risultato dal body
# Siamo già oltre il classico parser regex fragile.

"""
Per ogni riga di header e per ogni lista di possibili token divisi per tipo,
cerca il token con indice piu piccolo :

for row in self._header:
    for type in type_headers:
        try:
            token = min(
                (sub for sub in type if sub in row), 
                key = lambda sub: row.find(sub)
            )
            break
        except:
            continue
"""

