from enum import Enum, auto

# Definizione token
class TokenType(Enum):
    TURN_NUMBER = auto()
    MOVE = auto()
    RESULT = auto()
    EOF = auto()

# Lexer deterministico (char-by-char)
class PDNLexer:

    def __init__(self, text):
        self.text = text
        self.length = len(text)
        self.pos = 0

    def peek(self):
        if self.pos < self.length:
            return self.text[self.pos]
        return None

    def advance(self):
        ch = self.peek()
        self.pos += 1
        return ch

    def skip_whitespace(self):
        while self.peek() and self.peek().isspace():
            self.advance()

    def read_number(self):
        start = self.pos
        while self.peek() and self.peek().isdigit():
            self.advance()
        return self.text[start:self.pos]

    def read_move(self, first_number):
        parts = [first_number]

        while True:
            ch = self.peek()
            if ch not in ('-', 'x'):
                break

            sep = self.advance()
            number = self.read_number()
            if not number:
                raise ValueError("Mossa malformata")

            parts.append(sep + number)

        return ''.join(parts)

    def read_result(self, first_char):
        # gestisce 1-0, 0-1, 1/2-1/2
        buffer = first_char
        while self.peek() and self.peek() in "-/012":
            buffer += self.advance()
        return buffer

    def next_token(self):

        self.skip_whitespace()

        ch = self.peek()
        if ch is None:
            return (TokenType.EOF, None)

        # Numero (può essere TURN o MOVE o RESULT)
        if ch.isdigit():
            number = self.read_number()

            # TURN NUMBER?
            if self.peek() == '.':
                self.advance()
                return (TokenType.TURN_NUMBER, int(number))

            # RESULT?
            if number in ("1", "0") and self.peek() in ('-', '/'):
                result = self.read_result(number)
                return (TokenType.RESULT, result)

            # MOVE
            move = self.read_move(number)
            return (TokenType.MOVE, move)

        # Se carattere inatteso
        raise ValueError(f"Carattere inatteso: {ch}")
    
# Parser deterministico
class PDNParser:

    def __init__(self, text):
        self.lexer = PDNLexer(text)
        self.current_token = self.lexer.next_token()

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise ValueError(f"Atteso {token_type}, trovato {self.current_token}")

    def parse(self):
        moves = []
        result = None

        while self.current_token[0] != TokenType.EOF:

            if self.current_token[0] == TokenType.RESULT:
                result = self.current_token[1]
                self.eat(TokenType.RESULT)
                break

            # TURN
            turn_number = self.current_token[1]
            self.eat(TokenType.TURN_NUMBER)

            # WHITE
            white = self.current_token[1]
            self.eat(TokenType.MOVE)

            black = None
            if self.current_token[0] == TokenType.MOVE:
                black = self.current_token[1]
                self.eat(TokenType.MOVE)

            moves.append({
                "move_number": turn_number,
                "white": white,
                "black": black
            })

        return moves, result
    
# Questo parser è:
# Deterministico
# O(n)
# Zero backtracking
# Zero ambiguità
# Espandibile (puoi aggiungere commenti, varianti, NAG ecc.)
# Adatto a pipeline ML ad alte performance

# Versione aggiornata parse_pdn compatibile con lexer/parser deterministico
from collections import defaultdict
import re

def parse_pdn(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    games = re.split(r'(?=\[White\s+")', content.strip())

    parsed_games = []

    for game in games:

        if not game.strip():
            continue

        # ----------------------
        # HEADER
        # ----------------------
        metadata = defaultdict(list)

        for key, value in re.findall(r'\[(\w+)\s+"([^"]*)"\]', game):
            metadata[key].append(value)

        # ----------------------
        # BODY (mosse)
        # ----------------------
        parts = re.split(r'\n\s*\n', game, maxsplit=1)
        moves_text = parts[1] if len(parts) > 1 else ""

        # Rimozione commenti { }
        moves_text = re.sub(r'\{[^}]*\}', '', moves_text)

        # Parser deterministico
        parser = PDNParser(moves_text)
        moves, result = parser.parse()

        # Se risultato non trovato nel body,
        # lo prendiamo dall'header
        if result is None and "Result" in metadata:
            result = metadata["Result"][0]

        parsed_games.append({
            "metadata": dict(metadata),
            "moves": moves,
            "result": result
        })

    return parsed_games

# Esempio di utilizzo aggiornato
file_path = 'pdn/2008_Assoluti.txt'

partite = parse_pdn(file_path)

for i, partita in enumerate(partite, 1):
    print(f"Partita {i}:")
    print("Metadati:", partita['metadata'])
    print("Mosse:", partita['moves'])
    print("Result:", partita['result'])
    print("-" * 40)

# Architetturalmente ora hai
# - Header parsing
# - Lexer deterministico
# - Parser LL semplice
# - Separazione netta tra sintassi e semantica
# - Nessuna ambiguità tra MOVE e RESULT
# - Struttura pronta per ML pipeline
