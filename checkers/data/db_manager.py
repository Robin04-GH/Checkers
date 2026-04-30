import os
import sqlite3
import json
import zoneinfo
from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from checkers.constant import PATH_DATABASE
from checkers.data.data_interface import DataInterface
from checkers.engine.game.pieces import EnumPlayersColor
from checkers.engine.game.state import EnumResult, StateMove

@dataclass
class GameState:
    # Hint: a game in the database can be identified by order number ('id_game') 
    # or directly by the primary key ('pk_game') !
    id_game : str = ""
    pk_game : str = ""
    new_game : bool = False
    closed_game : bool = False
    in_restore : bool = False
    number_move : int = 1
    player_turn : EnumPlayersColor = EnumPlayersColor.P_LIGHT
    last_move_read : Optional[tuple[int, ...]] = None    

class DatabaseManager(DataInterface):
    """
    Database management class for match history.

    Database structure:
    - Players table (player data: pk='engine:name', statistics counters)
    - Games table (general game data: date, players, outcome)
    - Moves table + Move Steps (game move history)
    - States table (game board state history)

    Statistics are increased during the game if the export database is enabled. 
    Even if the game is imported from another database, only the information needed 
    to replicate the game (players' engine names and moves) is acquired; 
    the statistics contained in the import database are not accumulated, 
    and therefore only relate to the games saved on each database.

    Sequence of the main methods used in the logic :
     1) 'game_data()' : called first to check for the presence of a specified game. 
      If the check is done by order number, use '_game_order()', while '_game_exit()' 
      uses the primary key pk. Without specifying a game, the method generates the pk 
      as a datetime, which will then be needed by the remaining methods.    

     2) 'write_game()' : called every time a new game is exported. 
      It uses '_player_exist()' to check if the players playing the game are already present; 
      otherwise, '_add_player()' adds them to the players table.

     3) 'write_move()' : called to write moves.
      '_write_state()' is used internally to also print the board state to the console.
      When writing, the move number and turn attributes are used to control the arguments.
      The management of read moves includes several methods :
       - 'set_turn()': initializes the move number and turn, which is then incremented by 
       'next_turn()' within 'next_move()' to avoid adding them as arguments to the method 
       for each read, considering they are sequential.
      To manage undo moves, two methods that return the move are needed :
       - 'next_move()' advances the pointer to the move to be read with 'next_turn()'
       - 'get_move()' simply returns the last move pointed to by 'next_move()', that is
       'last_move_read'.      

     4) 'write_result()' : called to write the final outcome of the game and set the 
      end-of-game datatime, closing the possibility of adding further moves.

     5) 'add_stats_player()' : writes the statistics at the end of the game. 
      It uses '_get_id_players()' to retrieve the primary keys of the players playing the game.

     6) 'next_game()' : used in 'view' mode to increment the game ID. 
      If the order number is used, it checks for the next game and returns the incremented one. 
      If the primary key is used, it searches for the next game with ASC and returns the found 
      number. In both cases, if the next game is not present, it restarts from the first game 
      (cyclic 'view').      
    """

    def __init__(self):
        self._database : str = ""
        self._is_open : bool = False
        self._connection : sqlite3.Connection | None = None
        self._cursor : sqlite3.Cursor | None = None
        self._state = GameState()

    def open_data(self, filename:str, restore:str|None = None)->bool:
        self._database = filename
        try:
            if not os.path.isdir(PATH_DATABASE):
                raise ValueError(f"Database path does not exist : {PATH_DATABASE}")
            
            if restore:
                self._state.in_restore = True

            # 'isolation_level=None' puts the connection in 'autocommit': each statement is executed 
            # as a separate transaction unless you explicitly open a transaction (BEGIN … COMMIT).
            self._connection = sqlite3.connect(PATH_DATABASE + filename, isolation_level=None)
            self._cursor = self._connection.cursor()

            # In SQLite, you must explicitly enable referential constraints with PRAGMA foreign_keys = ON
            # for each connection. Place it immediately after connect() and in any case before executing:
            # - DDL (Data Definition Language) such as CREATE TABLE, ALTER TABLE, DROP TABLE
            # - DML (Data Manipulation Language) such as INSERT, UPDATE, DELETE, SELECT            
            self._cursor.execute("PRAGMA foreign_keys = ON")        

            # WAL improves reader/writer concurrency on local files, but increases
            # file journaling; not ideal on network file systems.
            # If the database is accessed only from the main thread and local file, 
            # WAL + short transactions is a good choice; it avoids concurrency complications.            
            self._cursor.execute("PRAGMA journal_mode = WAL")

            # 'synchronous' controls when SQLite calls fsync to ensure data is physically 
            # written to disk. Setting NORMAL synchronizes less frequently than FULL, 
            # making it faster.
            # There's a very low risk of losing recent transactions in the event of a power outage; 
            # it's not recommended except on network filesystems or if you have 
            # absolute durability requirements.
            self._cursor.execute("PRAGMA synchronous = NORMAL")

            # Hint: PRAGMAs like 'synchronous' and 'journal_mode' must be set on every connection 
            # because some PRAGMAs do not persist across connections !

            self._create_schema()
            self._is_open = True
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, open_data() : DB opening error {e}")
            self._is_open = False
        except Exception as e:
            print(f"Class DatabaseManager, open_data() : unexpected error {e}")
            self._is_open = False
        finally:
            if not self._is_open and self._connection:
                self._connection.close()
                self._connection = None
                self._cursor = None

        return self._is_open

    def close_data(self):
        if self._connection:
            try:
                self._connection.close()
            except sqlite3.Error as e:
                print(f"Class DatabaseManager, close_data() : error while closing DB {e}")
            finally:
                self._connection = None
                self._cursor = None
        self._is_open = False

    def is_open(self)->bool:
        return self._is_open

    # 'ON DELETE/UPDATE CASCADE' automates the removal/propagation of changes to children.
    # 'INTEGER PRIMARY KEY' is an alias for 'ROWID' and automatically generates a value 
    # if not provided.
    # 'AUTOINCREMENT' prevents reassignment of already used IDs (absolute monotonicity),
    # but adds overhead.
    # 'DEFAULT CURRENT_TIMESTAMP' for automatic values ​​at row creation
    # when the current UTC time is fine.

    def _create_schema(self):
        try:
            # Create tables only if they do not already exist

            # Table players
            # Hint: a player is identified by (engine, name). Therefore, across multiple 
            # databases, that player could have different 'id'!
            self._cursor.executescript("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    engine TEXT NOT NULL,
                    name TEXT NOT NULL,
                    wins INTEGER NOT NULL,
                    draws INTEGER NOT NULL,
                    losses INTEGER NOT NULL,
                    UNIQUE(engine, name)
                );
            """)

            # Table games
            # Hint: a game's 'pk' is specific to each database. So a game imported from one 
            # database with its own 'pk' is exported to another database with a different 'pk'!
            self._cursor.executescript("""
                CREATE TABLE IF NOT EXISTS games (
                    pk TEXT PRIMARY KEY,
                    player_light_id INTEGER NOT NULL,
                    player_dark_id INTEGER NOT NULL,
                    result TEXT,
                    started_at TEXT DEFAULT (datetime('now')),
                    finished_at TEXT,

                    FOREIGN KEY(player_light_id) REFERENCES players(id) ON DELETE CASCADE,
                    FOREIGN KEY(player_dark_id) REFERENCES players(id) ON DELETE CASCADE
                );
            """)

            # Table moves
            # Standardized scheme
            self._cursor.executescript("""
                CREATE TABLE IF NOT EXISTS moves (
                    id INTEGER PRIMARY KEY,
                    pk_game TEXT NOT NULL,
                    number_move INTEGER NOT NULL,
                    player_turn TEXT NOT NULL CHECK(player_turn IN ('P_LIGHT','P_DARK')),
                    notation TEXT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    origin_cell INTEGER NOT NULL,
                    moved_piece_id INTEGER NOT NULL,
                    promoted INTEGER NOT NULL CHECK(promoted IN (0,1)),

                    FOREIGN KEY(pk_game) REFERENCES games(pk) ON DELETE CASCADE
                );
            """)

            # Table Move Steps
            self._cursor.executescript("""
                CREATE TABLE IF NOT EXISTS move_steps (
                    id INTEGER PRIMARY KEY,
                    move_id INTEGER NOT NULL,
                    seq_index INTEGER NOT NULL,
                    destination_cell INTEGER NOT NULL,
                    captured_piece_id INTEGER,
                                    
                    FOREIGN KEY(move_id) REFERENCES moves(id) ON DELETE CASCADE
                );
            """)
            
            # Table States
            # Arrangement of pieces on the board after the move 'move_id'
            # Snapshot schema with JSON
            # Hint: the initial arrangement of the pieces is not saved !            
            self._cursor.executescript("""
                CREATE TABLE IF NOT EXISTS states (
                    id INTEGER PRIMARY KEY,
                    move_id INTEGER NOT NULL,
                    checkerboard JSON NOT NULL,
                                
                    FOREIGN KEY(move_id) REFERENCES moves(id) ON DELETE CASCADE
                );
            """)

            # Index                    
            self._cursor.executescript("""
                CREATE INDEX IF NOT EXISTS idx_engine_name ON players(engine, name);                                       
                CREATE INDEX IF NOT EXISTS idx_move_turn ON moves(pk_game, number_move, player_turn);
                CREATE INDEX IF NOT EXISTS idx_move_step ON move_steps(move_id, seq_index);
            """)            
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, _create_schema() : schema creation error {e}")
            if self._connection:
                self._connection.rollback()
            raise

    def _game_order(self, id_game: str)->str:
        if not self._is_open:
            raise RuntimeError("Database not open")

        if not id_game:
            return False

        try:
            self._cursor.execute("""
                SELECT pk FROM games
                ORDER BY pk ASC
                LIMIT 1 OFFSET ?-1
            """, (id_game,))

            row = self._cursor.fetchone()
            self._state.pk_game = row[0] if row else ""

            return self._state.pk_game
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, _game_order(), SQLite error {e}")
            raise

    def _game_exist(self, id_game: str)->bool:
        if not self._is_open:
            raise RuntimeError("Database not open")

        if not id_game:
            return False

        try:
            self._cursor.execute(
                "SELECT 1 FROM games WHERE pk = ? LIMIT 1",
                (id_game,)
            )

            return self._cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, _game_exist(), SQLite error {e}")
            raise

    def _generate_datetime(self)->str:
        # Generate datetime for primary key game (unique with microseconds).
        # Hint: only returned, not assigned to self.pk_game !        
        # return datetime.now().strftime("%Y%m%d%H%M%S%f") # but use local time
        return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f") # always UTC
    
    # if '_pk_game' is present (read from db or write after restore) 
    # only checks the presence of the match identifier, otherwise adds the 
    # new match row generating the unique '_pk_game' with '_generate_datetime()' !
    def game_data(self, id_game: str)->bool:
        if not self._is_open:
            raise RuntimeError("Database not open")

        if id_game:
            found : bool = False
            if len(id_game) == 20:
                # id_game as pk
                if self._game_exist(id_game):
                    self._state.id_game = ""
                    self._state.pk_game = id_game
                    self._state.new_game = False
                    found = True
            else:
                # id_game as order number
                pk = self._game_order(id_game)
                if pk:
                    self._state.id_game = id_game
                    self._state.pk_game = pk
                    self._state.new_game = False
                    found = True
            
            if found:
                # 'closed_game' setting to block writing moves and results
                self.set_closed_game()
                return True   

        # New game
        self._state.id_game = ""
        self._state.pk_game = self._generate_datetime()
        self._state.new_game = True
        self._state.closed_game = False
        return False

    def set_closed_game(self):
        try:
            self._cursor.execute("""
                    SELECT result, finished_at FROM games
                    WHERE pk = ?
                """, (self._state.pk_game,))
            row = self._cursor.fetchone()
            if row:                
                result, finished_at = row
                self._state.closed_game = True if result and finished_at else False
            else:
                self._state.closed_game = False
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, check_closed_game() : SQLite error {e}")
            raise

    # Match identification in a default database is done via 'pk' !
    def get_id_game(self)->str:
        return self._state.pk_game

    # When the game is over set 'id_game' or '_pk_game' to the next game
    def next_game(self, cyclic:bool = False)->str:
        if not self._is_open:
            raise RuntimeError("Database not open")

        # if 'id_game', ...
        if self._state.id_game:
            id_game = int(self._state.id_game)
            id_game += 1
            self._state.id_game = str(id_game)
            pk = self._game_order(self._state.id_game)
            if cyclic and not pk:
                self._state.id_game = "1"

            return self._state.id_game               

        # ... else '_pk_game'
        try:
            self._cursor.execute("""
                SELECT pk FROM games
                WHERE pk > ?
                ORDER BY pk ASC
                LIMIT 1
            """, (self._state.pk_game,))
            row = self._cursor.fetchone()

            # If there are no subsequent games, go back to the first (cyclic)
            if cyclic and row is None:
                self._cursor.execute("""
                    SELECT pk FROM games
                    ORDER BY pk ASC
                    LIMIT 1
                """)
                row = self._cursor.fetchone()

            self._state.pk_game = row[0] if row else ""
            return self._state.pk_game

        except sqlite3.Error as e:
            print(f"Class DatabaseManager, next_game() : SQLite error {e}")
            raise

    # Returns tuples in (P_LIGHT, P_DARK) order, with engine and name
    def get_pk_players(self)->tuple[str, str, str, str]:
        if not self._is_open:
            raise RuntimeError("Database not open")        
        
        try:
            self._cursor.execute("""
                SELECT 
                    pl.engine AS light_engine,
                    pl.name   AS light_name,
                    pd.engine AS dark_engine,
                    pd.name   AS dark_name
                FROM games g
                JOIN players pl ON g.player_light_id = pl.id
                JOIN players pd ON g.player_dark_id = pd.id
                WHERE g.pk = ?;
            """, (self._state.pk_game,))
            return self._cursor.fetchone()    
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, get_pk_players() : SQLite error {e}")
            raise    

    def _get_id_players(self)->tuple[int, int]:
        if not self._is_open:
            raise RuntimeError("Database not open")        
        
        try:
            self._cursor.execute("""
                SELECT 
                    player_light_id,
                    player_dark_id
                FROM games g
                WHERE g.pk = ?;
            """, (self._state.pk_game,))
            return self._cursor.fetchone()    
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, _get_id_players() : SQLite error {e}")
            raise    

    def get_stats_player(self, player:EnumPlayersColor)->tuple[int, int, int]:
        if not self._is_open:
            raise RuntimeError("Database not open")        
        
        player_light_id, player_dark_id = self._get_id_players()
            
        id_player : int = (
            player_light_id 
            if player == EnumPlayersColor.P_LIGHT 
            else player_dark_id
        )
        try:
            self._cursor.execute("""
                SELECT 
                    wins, draws, losses
                FROM players
                WHERE id = ?;
            """, (id_player,))
            return self._cursor.fetchone()    
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, get_stats_player() : SQLite error {e}")
            raise    

    def add_stats_player(self, player:EnumPlayersColor, add_stats:tuple[int, int, int]):
        if not self._is_open:
            raise RuntimeError("Database not open")        
        
        player_light_id, player_dark_id = self._get_id_players()

        id_player : int = (
            player_light_id 
            if player == EnumPlayersColor.P_LIGHT 
            else player_dark_id
        )

        add_wins, add_draws, add_losses = add_stats
        try:
            self._cursor.execute("BEGIN IMMEDIATE")

            self._cursor.execute("""
                UPDATE players
                SET
                    wins = wins + ?, 
                    draws = draws + ?, 
                    losses = losses + ?
                WHERE id = ?;
            """, (add_wins, add_draws, add_losses, id_player,))

            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, get_stats_player() : SQLite error {e}")
            raise            

    def _player_exist(self, engine:str, name:str)->int | None:
        self._cursor.execute("""
            SELECT id FROM players 
            WHERE engine = ? AND name = ?;
        """, (engine, name))
        row = self._cursor.fetchone()
        return row[0] if row is not None else None

    def _add_player(self, engine:str, name:str)->int | None:
        if not self._is_open:
            raise RuntimeError("Database not open")
    
        try:
            self._cursor.execute("""
                INSERT INTO players (engine, name, wins, draws, losses) 
                VALUES (?, ?, ?, ?, ?) 
                RETURNING id
            """, (engine, name, 0, 0, 0))
            row = self._cursor.fetchone()
            return row[0] if row is not None else None
        except sqlite3.IntegrityError as e:
            print(f"Class DatabaseManager, _add_player() : player duplicato {engine}, {name}")
            raise
        #except sqlite3.OperationalError as e:
        #    print(f"Operational error {e} !")
        except sqlite3.Error as e:
            print(f"Errore generico : {e} !")
            raise ValueError(f"Class DatabaseManager, _add_player() : insert error !")
        
    def find_last_move(self)->tuple[int, EnumPlayersColor]:
        try:        
            self._cursor.execute("""
                SELECT number_move, player_turn FROM moves 
                WHERE pk_game = ?
                ORDER BY number_move DESC, player_turn ASC
                LIMIT 1
            """, (self._state.pk_game,))

            row = self._cursor.fetchone()

            if row:
                number, turn = row
                if turn == EnumPlayersColor.P_LIGHT:
                    turn = EnumPlayersColor.P_DARK
                else:
                    number += 1
                    turn = EnumPlayersColor.P_LIGHT
                ret = (number, turn)
            else:
                ret = (1, EnumPlayersColor.P_LIGHT)
                
            return ret
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, set_turn(), SQLite error {e}")
            raise

    def write_game(self, id_game:str, pk_players:tuple[str,str,str,str]):
        if not self._is_open:
            raise RuntimeError("Database not open")
    
        # Check if the pk_game saved with 'game_data()' matches the 'id_game' passed as argument
        if id_game != self._state.pk_game:
            raise ValueError(f"Class DatabaseManager, write_game() : game ID mismatch !")

        # Avoid writing if game already present (export from restore)
        if not self._state.new_game:
            # Initialize next move by searching for all the ones already written
            self._state.number_move, self._state.player_turn = self.find_last_move()
            return

        # Initialize move attributes to check argument sequentiality in the 'write_move()'
        self._state.number_move = 1
        self._state.player_turn = EnumPlayersColor.P_LIGHT

        light_engine, light_name, dark_engine, dark_name = pk_players
        try:
            self._cursor.execute("BEGIN IMMEDIATE")        

            player_light_id = self._player_exist(light_engine, light_name)
            if player_light_id is None:
                player_light_id = self._add_player(light_engine, light_name)

            player_dark_id = self._player_exist(dark_engine, dark_name)
            if player_dark_id is None:
                player_dark_id = self._add_player(dark_engine, dark_name)

            self._cursor.execute("""
                INSERT INTO games (pk, player_light_id, player_dark_id)
                VALUES (?, ?, ?)
            """, (self._state.pk_game, player_light_id, player_dark_id))

            # self._cursor.execute("COMMIT")
            self._connection.commit()
        except Exception as e:
            print(f"Class DatabaseManager, write_game() error: {e}")
            if self._connection:
                self._connection.rollback()
            raise

    def set_turn(self, number_move:int, player_turn:EnumPlayersColor):
        self._state.number_move = number_move
        self._state.player_turn = player_turn

        try:
            # Check attendance for previous turn
            if self._state.number_move == 1 and self._state.player_turn == EnumPlayersColor.P_LIGHT:
                return 
            
            if player_turn == EnumPlayersColor.P_DARK:
                player_turn = EnumPlayersColor.P_LIGHT
            else:
                number_move -= 1
                player_turn = EnumPlayersColor.P_DARK

            self._cursor.execute("""
                SELECT 1 FROM moves 
                WHERE pk_game = ? AND number_move = ? AND player_turn = ?;
            """, (self._state.pk_game, number_move, player_turn.name))

            found = self._cursor.fetchone() is not None
            if not found:
                raise ValueError(f"Class DatabaseManager, set_turn() : previous number_move / player_turn not found !")
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, set_turn(), SQLite error {e}")
            raise

    def next_turn(self):
        if self._state.player_turn == EnumPlayersColor.P_LIGHT:
            self._state.player_turn = EnumPlayersColor.P_DARK
        else:
            self._state.player_turn = EnumPlayersColor.P_LIGHT
            self._state.number_move += 1

    def get_move(self)->Optional[tuple[int, ...]]:
        return self._state.last_move_read

    def next_move(self)->Optional[tuple[int, ...]]:
        if not self._is_open:
            raise RuntimeError("Database not open")

        try:
            # Recover the main move
            self._cursor.execute("""
                SELECT id, origin_cell 
                FROM moves
                WHERE pk_game = ? AND number_move = ? AND player_turn = ?
                LIMIT 1
            """, (self._state.pk_game, self._state.number_move, self._state.player_turn.name))

            row = self._cursor.fetchone()
            if row is None:
                return None

            move_id, origin_cell = row
            move_cells = [origin_cell]

            # Retrieve ordered steps
            self._cursor.execute("""
                SELECT destination_cell
                FROM move_steps
                WHERE move_id = ?
                ORDER BY seq_index ASC
            """, (move_id,))

            for (dest,) in self._cursor.fetchall():
                move_cells.append(dest)
            move = tuple(move_cells)

            # Update internal status
            self._state.last_move_read = move
            self.next_turn()
            return move
        except sqlite3.Error as e:
            print(f"[DatabaseManager] SQLite error in next_move(): {e}")
            raise
    
    @staticmethod
    def notation_move(state_move: StateMove)->str:
        separator : str = "x" if state_move.move.captures else "-"
        return separator.join(str(cell+1) for cell in state_move.move.as_tuple())

    def write_move(
        self,
        number_move: int,
        player_turn: EnumPlayersColor,
        state_move: StateMove,
        state_checkerboard: list[int] | None = None
    ):
        if not self._is_open:
            raise RuntimeError("Database not open")

        if state_move is None:
            return

        # 'closed_game' verification open
        if self._state.closed_game:
            raise ValueError(f"Class DatabaseManager, write_move() : match already finished !")

        # Check the sequence of the arguments turn move
        if self._state.number_move != number_move or self._state.player_turn != player_turn:
            raise ValueError(f"Class DatabaseManager, write_move() : move number and turn mismatch !")

        try:
            self._cursor.execute("BEGIN IMMEDIATE")

            # Inserting the main move
            self._cursor.execute("""
                INSERT INTO moves (
                    pk_game, number_move, player_turn, notation,
                    origin_cell, moved_piece_id, promoted
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                self._state.pk_game,
                number_move,
                player_turn.name,
                DatabaseManager.notation_move(state_move),
                state_move.move.origin,
                state_move.moved_piece,
                int(state_move.promoted_king)
            ))

            row = self._cursor.fetchone()
            if row is None:
                raise RuntimeError("Failed to insert move")

            move_id = row[0]

            # Inserting the move step
            for idx, dest_cell in enumerate(state_move.move.destinations, start=1):
                captured_piece_id = (
                    state_move.captured_pieces[idx - 1]
                    if idx - 1 < len(state_move.captured_pieces)
                    else None
                )

                self._cursor.execute("""
                    INSERT INTO move_steps (
                        move_id, seq_index, destination_cell, captured_piece_id
                    )
                    VALUES (?, ?, ?, ?)
                """, (move_id, idx, dest_cell, captured_piece_id))

            # Writing the checkerboard state
            if state_checkerboard is not None:
                self._write_state(move_id, state_checkerboard)

            self._connection.commit()

            # Next move round update for write check
            self.next_turn()
        except Exception as e:
            print(f"Class DatabaseManager, write_move() : error {e}")
            if self._connection:
                self._connection.rollback()
            raise
            
    def _write_state(self, move_id:int, state_checkerboard:list[int]):
        if not self._is_open:
            raise RuntimeError("Database not open")

        if not isinstance(state_checkerboard, list):
            raise ValueError("state_checkerboard must be a list")

        try:
            json_state = json.dumps(state_checkerboard)

            self._cursor.execute("""
                INSERT INTO states (move_id, checkerboard)
                VALUES (?, ?)
            """, (move_id, json_state))

        except sqlite3.Error as e:
            print(f"Class DatabaseManager, _write_state() : SQLite error {e}")
            raise

    def read_state(self, number_move:int, player_turn:EnumPlayersColor)->list[int] | None:
        if not self._is_open:
            raise RuntimeError("Database not open")

        try:
            self._cursor.execute("""
                SELECT s.checkerboard
                FROM states s
                JOIN moves m ON s.move_id = m.id
                WHERE m.pk_game = ? AND m.number_move = ? AND m.player_turn = ?
                LIMIT 1
            """, (self._state.pk_game, number_move, player_turn.name))

            row = self._cursor.fetchone()

            if row is None:
                return None
            return json.loads(row[0])
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, read_state() : SQLite error {e}")
            raise

    def get_result(self)->EnumResult:
        if not self._is_open:
            raise RuntimeError("Database not open")

        try:
            self._cursor.execute("""
                SELECT result FROM games
                WHERE pk = ?
                LIMIT 1
            """, (self._state.pk_game,))

            row = self._cursor.fetchone()
            if row is None or row[0] is None:
                return EnumResult.R_NONE
            return EnumResult[row[0]]
        except sqlite3.Error as e:
            print(f"Class DatabaseManager, get_result() : SQLite error {e}")
            raise

    def write_result(self, result:EnumResult):
        if not self._is_open:
            raise RuntimeError("Database not open")

        # 'closed_game' verification open
        if self._state.closed_game:
            raise ValueError(f"Class DatabaseManager, write_result() : match already finished !")

        try:
            self._cursor.execute("BEGIN IMMEDIATE")

            self._cursor.execute("""
                UPDATE games
                SET result = ?, finished_at = ?
                WHERE pk = ?
            """, (result.name, DatabaseManager.utc_sqlite_now(), self._state.pk_game))

            self._connection.commit()
            self._state.closed_game = True
        except Exception as e:
            print(f"Class DatabaseManager, write_result() : error {e}")
            if self._connection:
                self._connection.rollback()
            raise

    @staticmethod
    def utc_sqlite_now()->str:
        # All datetimes are homogeneous with UTC. Convert locally only on output (if needed),
        # without T, without offset, without +00:00 :
        # - timezone.utc forces Python to use UTC
        # - strftime() converts to the SQLite format used in CREATE with '(datetime('now'))'        
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Method to add an offset to the output
    def to_local(dt_str, tz="Europe/Rome")->str:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.astimezone(zoneinfo.ZoneInfo(tz)).isoformat(timespec="seconds")

    @staticmethod
    def parse_iso(dt:str)->datetime:
        return datetime.fromisoformat(dt.replace(" ", "T"))
