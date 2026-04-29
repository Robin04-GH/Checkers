import re
import io
import enum
from typing import Optional
from checkers.constant import PATH_PDN
from checkers.data.data_interface import DataInterface
from checkers.engine.game.pieces import EnumPlayersColor
from checkers.engine.game.state import EnumResult, StateMove
from checkers.data.db_manager import DatabaseManager
from collections import defaultdict
#from dataclasses import dataclass, field

#@dataclass(slots=True, eq=False)
#class PdnLexer:
#    _moves: str = ""
#    _length: int = 0
#    _pos: int = 0
#    _result: str = ""
#    _moves_chunks:list[str] = field(default_factory=list, repr=False)

class PdnLexer:
    __slots__ = ("_moves", "_length", "_pos", "_result", "_moves_chunks")

    _moves: str
    _length: int
    _pos: int
    _result: str
    _moves_chunks: list[str]

    def __init__(self):
        self._moves = ""
        self._length = 0
        self._pos = 0
        self._result = ""
        self._moves_chunks = []

    def clear_moves(self):
        self._moves_chunks.clear()

    def reset(self):
        self._moves = ""
        self._length = 0
        self._pos = 0
        self._result = ""
        self.clear_moves()

    def set_moves(self, text:str):        
        self._moves_chunks.append(text)

    def set_length(self):
        self._moves = ' '.join(self._moves_chunks)
        self.clear_moves()        
        self._length = len(self._moves)

    def get_result(self)->str:
        # '1-0', '2-0', '0-1', '0-2', '1/2-1/2', '1-1' (specified result)
        # '*' (terminator)
        # '' (unspecified result)
        return self._result
    
    def peek(self)->str | None:
        pos = self._pos
        if pos < self._length:
            return self._moves[pos]
        return None        

    def advance(self)->str | None:
        ch = self.peek()
        self._pos += 1
        return ch

    def skip_whitespace(self):
        ch : str = self.peek()
        while ch and ch.isspace():
            self.advance()
            ch = self.peek()

    def read_result(self, first_char:str):
        # Specified result '1-0', '2-0', '0-1', '0-2', '1/2-1/2', '1-1'
        possible_results : list[str] = ["1-0", "2-0", "0-1", "0-2", "1/2-1/2", "1-1"] 

        buffer = [first_char]
        ch : str = self.peek()
        while ch and ch in "-/012":
            buffer.append(self.advance())
            ch = self.peek()

        result = ''.join(buffer)
        return (
            result 
            if result in possible_results
            else ""
        )            
    
    def seek_number(self)->bool:
        self.skip_whitespace()

        ch = self.peek()
        if ch is None:
            return False
        
        if not ch.isdigit():
            if ch == '*':
                self._result = ch
            return False
        else:
            return True

    def read_number(self)->str | None:
        start = self._pos
        ch : str = self.peek()
        while ch and ch.isdigit():
            self.advance()
            ch = self.peek()
        return self._moves[start:self._pos]

    def read_move(self)->tuple[int, ...] | None:
        while True:
            if not self.seek_number():
                return None

            number : str | None = self.read_number()

            # skip turn
            ch : str = self.peek()
            if ch == '.':
                self.advance()
            else:
                break

        # Hint: the engine  counts cells in base-0, not base-1 like pdn !
        cells = [int(number)-1]

        # if 'number' is 0 or 1 or 2 it could be the result
        if number in ("0", "1", "2"):
            pos = self._pos
            self._result = self.read_result(number)
            if self.get_result():
                return None
            else:
                self._pos = pos

        while True:
            ch = self.peek()
            if ch not in ('-', 'x'):
                break

            sep = self.advance()
            number = self.read_number()
            if not number:
                raise ValueError("Malformed move !")

            cells.append(int(number)-1)
        
        return tuple(cells)
        
    # Place the cursor on 'number_move' to later read the 'player_turn' move
    def seek_move(self, number_move:int, player_turn:EnumPlayersColor)->bool:
        # Hint: determine whether the .pdn file specifies the move number, ...
        if self._moves.find('1.') >= 0:
            str_number_move = str(number_move)
            index = self._moves.find(str_number_move + '.')
            if index >= 0:        
                self._pos = index + len(str_number_move) + 1
            else:
                return False
        else:
            # ... otherwise search without index
            jump_move = (number_move - 1) * 2
            while jump_move > 0:
                if not self.read_move():
                    return False
                jump_move -= 1

        if player_turn == EnumPlayersColor.P_LIGHT:
            return True

        # light player move absent     
        if not self.read_move():
            return False
        else:
            return True

# Class that defines the type of PDN row read by the cursor
@enum.unique
class EnumRowType(enum.Enum):
    R_NONE = 0
    R_HEADER = 1
    R_MOVE = 2

class PdnManager(DataInterface):
    """
    Class for parsing game formats in PDN.
    Used for imports/exports game on PDN.
    """

    def __init__(self):
        self._pdn_name : str = ""
        self._pdn_game : int = 0
        self._file = None
        self._in_restore : bool = False

        self._raw_line : str = ""
        self._buf_line : str = ""
        self._curly_level : int = 0
        self._index_start : int = 0
        self._index_stop : int = 0

        self._light_players : str = ""
        self._dark_players : str = ""
        self._result : str = ""        
        self._counter_game : int = 0

        self._max_games : int = 0
        self._max_number_move : int = 0
        self._max_player_turn : EnumPlayersColor = EnumPlayersColor.P_LIGHT
        self._max_result : EnumResult = EnumResult.R_NONE

        self._row_type : EnumRowType = EnumRowType.R_NONE

        # In import, they are used to read moves, setting the initial turn at the start of the 
        # game, with implicit increment in 'next_move()' to avoid arguments in the method.
        # In export, however, the caller 'write_move()' passes the turn arguments and attributes.
        # '_number_move'/'_player_turn' are used to check sequentiality.
        self._number_move : int = 1
        self._player_turn : EnumPlayersColor = EnumPlayersColor.P_LIGHT  

        self.lexer : PdnLexer = PdnLexer()  
        self.last_move : Optional[tuple[int, ...]] = None

    def open_data(self, filename:str, restore:str|None = None)->bool:
        # Check presence and opening of PDN files
        self._pdn_name = filename
        if restore:
            self._in_restore = True

        try:
            self._file = open(PATH_PDN + self._pdn_name, 'a+', encoding='iso-8859-1')

            # Game count contained in the file (self._max_game), and moves present in the last game
            self._search_max_games_moves()
            return True
        except:            
            self.close_data()
            return False

    def close_data(self):
        if self._file:
            self._file.close()

    def is_open(self)->bool:
        return not self._file.closed

    def game_data(self, id_game:str)->bool:
        """
        Positioning file cursor at the requested game_id.

        Hint: a 'game_id' is relative to the PDN file. Therefore, a game imported from a 
        PDN with a 'game_id' will be appended to the export PDN with a 'game_id' that 
        will generally be different !
        """

        # Hint: if 'id_game' is empty, the game is appended. 'id_game' is calculated based 
        # on the number of games already saved in the file (self._max_game), performing a full 
        # scan only in open_data().
        # .pdn files can only write to 'append'; intermediate games cannot be added.
        # When specified, a check is made to ensure that '_pdn_game' is actually the last one; 
        # otherwise, it is assigned to 'self._max_game + 1' !
        if id_game and not self._in_restore:
            # Import
            self._pdn_game = max(1, int(id_game) if id_game.isdigit() else 1)
            if self._pdn_game > self._max_games:
                return False
            
            return self._search_game(self._pdn_game)
        else:
            # Export
            # When writing, '_number_move' and '_player_turn' are only used for method 
            # verification 'write_move()'
            self._pdn_game = self._max_games
            # In import a 'id_game' is always specified, in export only in the case of a restore.
            if id_game:
                self._number_move = self._max_number_move
                self._player_turn = self._max_player_turn
            else:
                self._pdn_game += 1
                self._number_move = 1
                self._player_turn = EnumPlayersColor.P_LIGHT

            # Hint: to avoid SEEK_END, the appended file is opened directly.
            # ('a+' to also be able to read) !
            # self._file.seek(0, io.SEEK_END)
            return True

        # if not self._search_game(self._pdn_game):
        #     raise ValueError(f"Game {self._pdn_game} not present in file {self._pdn_name} !")
        
        # Test
        # self.set_turn(27, EnumPlayersColor.P_LIGHT)
        # for i in range(10):
        #     move = self.next_move()
        
    def get_id_game(self)->str:
        return str(self._pdn_game)

    def next_game(self, cyclic:bool = False)->str:
        self._pdn_game += 1
        if cyclic and self._pdn_game > self._max_games:
            self._pdn_game = 1
        return str(self._pdn_game)

    # Returns tuples in (P_LIGHT, P_DARK) order, with engine and name
    def get_pk_players(self)->tuple[tuple[str, str, str, str]]:
        # Hint: engines are not present in PDN !
        return None, self._light_players, None, self._dark_players

    def set_turn(self, number_move:int, player_turn:EnumPlayersColor):
        self._number_move = number_move
        self._player_turn = player_turn
        if not self.lexer.seek_move(self._number_move, self._player_turn):
            raise ValueError(f"Class PdnManager, set_turn() : number_move / player_turn not found !")

    def next_turn(self):
        if self._player_turn == EnumPlayersColor.P_LIGHT:
            self._player_turn = EnumPlayersColor.P_DARK
        else:
            self._player_turn = EnumPlayersColor.P_LIGHT
            self._number_move += 1

    def get_move(self)->Optional[tuple[int, ...]]:
        return self.last_move

    def next_move(self)->Optional[tuple[int, ...]]:
        move = self.lexer.read_move()

        # Some .pdn files do not complete the game according to the rules and report the result 
        # prematurely. If there are no further moves, and there is a valid result (excluding '*') 
        # in the header or at the end of the move buffer, the game will still be forced to end.
        if move is not None:
            # print(f"Move {self._number_move} : {self._player_turn} = {move}")
            self.next_turn()        

        self.last_move = move

        return move
    
    def get_result(self)->EnumResult:
        # The result is considered to be the one specified at the end of the moves if present 
        # (excluding '*'), otherwise the one in the header
        result : str = self.lexer.get_result()
        if result == '' or result == '*':
            result = self._result

        enum_result : EnumResult = EnumResult.R_NONE
        match result:
            case '1-0' | '2-0':
                enum_result = EnumResult.R_LIGHT
            case '0-1' | '0-2':
                enum_result = EnumResult.R_DARK
            case '1/2-1/2' | '1-1':
                enum_result = EnumResult.R_PARITY
            case '*':
                enum_result = EnumResult.R_STAR
            case _:                
                enum_result = EnumResult.R_NONE                
        
        return enum_result

    def write_game(self, id_game:str, pk_players:tuple[str,str,str,str]):
        if self._in_restore:
            return

        header : list[str] = []

        event : str = ""
        datetime : str = DatabaseManager.utc_sqlite_now()
        light_engine, light_name, dark_engine, dark_name = pk_players
        result : str = ""

        header.append(f'[Event "{event}"]\n')
        header.append(f'[Date "{datetime}"]\n')
        header.append(f'[White "{light_name}"]\n')
        header.append(f'[Black "{dark_name}"]\n')
        header.append(f'[Result "{result}"]\n')

        self._file.writelines(header)

    def write_move(
            self, 
            number_move:int, player_turn:EnumPlayersColor, state_move:StateMove,
            state_checkerboard:list[int] = None
        ):
        if self._number_move != number_move or self._player_turn != player_turn:
            raise ValueError(f"Class PdnManager, write_move() : move number and turn mismatch !")

        self._in_restore = False
        move_str : str = ""
        if player_turn == EnumPlayersColor.P_LIGHT:
            separator = "\n" if number_move % 5 == 1 else " "
            move_str += f"{separator}{number_move}."
        move_str += " " + DatabaseManager.notation_move(state_move)

        self._file.write(move_str)
        # Increase move and turn number for subsequent checks
        self.next_turn()

    def write_result(self, result:EnumResult):
        # If '_in_restore' is still present in 'write_result()', it means that no moves have 
        # been written and therefore the result should not be written either.
        # However, it must be reset to be able to write the header for the next game.
        if self._in_restore:
            self._in_restore = False
            return

        results : dict[EnumResult, str] = {
            EnumResult.R_LIGHT : "1-0",
            EnumResult.R_DARK : "0-1", 
            EnumResult.R_PARITY : "1/2-1/2",
            EnumResult.R_STAR : "*"
        }
        self._file.write(" " + results.get(result, "") + "\n\n")

    def _comment_exclusion(self) -> str:
        """
        Stack-based linear parser for comment removal
        PDN line reading excluding spaces at the ends and comments delimited by { ... },
        even nested and across multiple lines
        """

        line : str = self._raw_line
        level : int = self._curly_level
        out : list[str] = []

        for ch in line:
            if ch == '{':
                level += 1
                continue

            if ch == '}':
                if level > 0:
                    level -= 1
                continue

            if level == 0:
                out.append(ch)

        self._curly_level = level

        result : str = ''.join(out).strip()
        return result

    def _reset_file(self):
        self._curly_level = 0
        self._counter_game = 0
        self.lexer.clear_moves()
        self._row_type : EnumRowType = EnumRowType.R_NONE
        self._buf_line = ""

    def _parser_headers(self):
        """
        Interpretation of header lines, delimited by [ ... ] only for the searched match.
        If present and recognized, the following header types are saved 
        but are not relevant for PDN management:
        - header_light
        - header_dark
        - header_result

        Hint: header lines are not necessarily always in the same order and may use
        different tokens for each type!
        """

        # header types
        header_light = ["White", "Bianco"]
        header_dark = ["Black", "Nero"]
        header_event = ["Event", "Dati"]
        header_site = ["Site", "Localita"]
        header_round = ["Round", "Turno"]
        header_date = ["Date", "Anno"]
        header_result = ["Result", "Esito", "Risultato"]
        header_gametype = ["GameType", "ECO", "Apertura"]

        header_types : dict[str, list[str]] = {
            "_light_players" : header_light,
            "_dark_players" : header_dark,
            "_result" : header_result
        }

        metadata = defaultdict(list)
        for key, value in re.findall(r'\[(\w+)\s+"([^"]*)"\]', self._buf_line):
            metadata[key].append(value)
        
        for key in metadata.keys():
            for attr, type in header_types.items():
                if key in type:
                    setattr(self, attr, metadata[key][0])
                    break
        
    def _search_max_games_moves(self):
        # Count of matches present in the file
        self._file.seek(0)
        self._pdn_game = 999999
        self._search_game(self._pdn_game, True)
        self._max_games = self._counter_game

        if self._max_games > 0:
            # Count of moves in the last game
            # self.set_turn(1, EnumPlayersColor.P_LIGHT)
            while self.next_move():
                pass

            self._max_number_move = self._number_move
            self._max_player_turn = self._player_turn
            self._max_result = self.get_result()

        # Restore file pointer for possible reading
        self._file.seek(0)
        self._reset_file()

    def _search_game(self, pdn_game:int, all:bool = False)->bool:
        """
        Game recognition based on alternating header lines and moves.
        A non-empty line filtered by spaces at the ends and comments can be:
        - when delimited by [ ... ], header,
        - otherwise it is considered a move.
        """

        first : bool = True

        # Repositioning file cursor to the beginning already beyond the searched game
        if self._counter_game >= self._pdn_game:
            self._file.seek(0)
            self._reset_file()
        else:
            self.lexer.clear_moves()

        self._light_players = ""
        self._dark_players = ""
        self._result = ""
        self.lexer.reset()

        while self._counter_game < self._pdn_game:

            # search for new game
            while True:
                # At startup I avoid rereading 'self._raw_line' from file 
                # if it is already present in 'self._buf_line' from the previous search
                if not first or not self._buf_line or self._row_type != EnumRowType.R_HEADER: 
                    self._raw_line = self._file.readline()

                    # If EOF header missing searched
                    if not self._raw_line:
                        self.lexer.set_length()
                        # Checking only the '_counter_game' without the '_row_type' allows 
                        # you to also find games with only the header and no moves yet
                        return (
                            True 
                            if self._counter_game == self._pdn_game #and self._row_type == EnumRowType.R_MOVE
                            else False
                        )

                    self._buf_line = self._comment_exclusion()

                first = False

                # Check if empty line
                if self._buf_line:
                    if self._buf_line[0] == '[' and self._buf_line[-1] == ']':
                        # header row
                        if self._row_type != EnumRowType.R_HEADER:
                            self._row_type = EnumRowType.R_HEADER
                            if all:
                                self.lexer.set_length()
                            self._counter_game += 1
                            # I exit the loop at the first line of the header of the 
                            # game following the one I'm looking for
                            if self._counter_game > self._pdn_game:
                                break

                        if self._counter_game == self._pdn_game and not all:
                            self._parser_headers()                            
                    else:
                        # line moves
                        if self._row_type == EnumRowType.R_HEADER:
                            self._row_type = EnumRowType.R_MOVE
                        elif self._row_type == EnumRowType.R_NONE:
                            # As long as there are no previous header lines, 
                            # discard any moved lines
                            continue  

                        if self._counter_game == self._pdn_game or all:
                            # append other lines moved in stream
                            self.lexer.set_moves(self._buf_line)

        self.lexer.set_length()
        return True
    