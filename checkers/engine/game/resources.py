import random
from typing import Optional
from checkers.config_manager import EnumExecutionMode, ConfigManager
from checkers.engine.game.state import State
from checkers.data.db_manager import DatabaseManager
from checkers.data.pdn_manager import PdnManager
from checkers.data.data_interface import DataInterface
from checkers.engine.inference_interface import InferenceInterface
from checkers.engine.inference_factory import InferenceFactory

class Resources:
    """
    The "history_database" is optional and must be enabled to archive game data or
    retrieve data in 'view' mode.
    The "restore" option can be applied to "play" and "view" modes. It also works without
    enabling archives through .json files saved in /restores.
    Using "view" mode requires the availability of a database for reading
    games, which can be created by playing a match with "history_datase"
    enabled, or by importing PDN (Portable Drafts Notation) formats.

    Possible configurations : 
    <play/view>   <restore>   <history>
          P           -           -
          V           -           -       Not possible !    
          P           X           -
          V           X           -       Not possible !
          P           -           X
          V           -           X
          P           X           X
          V           X           X
    """

    def __init__(self, config:ConfigManager, state:State):
        self.config = config
        self.state = state
        self.db_in_read : bool = False
        self.db_manager : DataInterface | None = None
        self.pdn_manager : DataInterface | None = None        
        self.restore : Optional[str] = self.config.restore_name
        self.player_light : str = self.state.build_pk_player(self.config.player1_engine, self.config.player1_name)
        self.player_dark  : str = self.state.build_pk_player(self.config.player2_engine, self.config.player2_name)
        self.pk_game : Optional[str] = self.config.pk_game
        # Testable determinism
        self.rng = random.Random(self.config.seed)
        # Inference cache
        self._inference_cache : dict[str, InferenceInterface] = {}

    def __enter__(self):
        self._initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._finalize()

    def _validate_resource(
        self, arg_db_name : str, arg_pk_game : str, arg_pdn_name : str, arg_pdn_game :str
    )->tuple[str, str, str, str, bool]:
        
        # Hint: different from empty string only in 'play' with history active or in 'view'!        
        db_name : str = ""
        pk_game : str = ""
        pdn_name : str = ""
        pdn_game : str = ""
        db_in_read : bool = False
        
        if (
            self.config.execution_mode != EnumExecutionMode.PLAY and 
            self.config.execution_mode != EnumExecutionMode.VIEW
        ):
            raise ValueError(f"Mode error !")
        
        if self.config.execution_mode == EnumExecutionMode.VIEW:
            if arg_pdn_name:
                if not arg_pdn_game:
                    raise ValueError(
                        "Config error : mode 'view' from 'import_pdn_name' without 'pdn_game' !"
                    )
                
                pdn_name = arg_pdn_name
                pdn_game = arg_pdn_game
            else:
                if not arg_db_name:
                    raise ValueError(
                        "Config error : mode 'view' without resource: 'import_pdn_name' or 'history_db_name' !"
                    )
                if not arg_pk_game:
                    raise ValueError(
                        "Config error : mode 'view' from 'history_db_name' without 'pk_game' !"
                    )
                db_in_read = True

        # While PDN can only be used in 'view' mode, the DB can also be used in 'play' mode
        if arg_db_name:
            db_name = arg_db_name
        if arg_pk_game:
            pk_game = arg_pk_game

        return (db_name, pk_game, pdn_name, pdn_game, db_in_read)        

    def _initialize(self):
        """
        Resources initialization context : 
         1) if restore is enabled, acquire data in State from /restores, otherwise only the
            database/pdn name, then save it in State
         2) open database/pdn if present
        """
        
        # If restore is enabled, the restart will acquire the data saved in /restores,
        # which partially overwrites the data in the configuration file
        if self.restore != None:
            self.state.restore(self.restore)

            (
                self.state.database, 
                self.state.pk_game, 
                self.state.pdn, 
                self.state.pdn_game, 
                self.db_in_read
            ) = self._validate_resource(    
                self.state.database,
                self.state.pk_game,
                self.state.pdn,
                self.state.pdn_game
            )

        else: 
            # Getting sources name on startup without restoring   
            # The variables with the names of the db/pdn and identifiers game are kept saved in State
            
            (
                self.state.database, 
                self.state.pk_game, 
                self.state.pdn, 
                self.state.pdn_game, 
                self.db_in_read 
            ) = self._validate_resource(            
                self.config.history_db_name,
                self.config.pk_game,
                self.config.import_pdn_name,
                self.config.pdn_game
            )

        # Opening database at startup, if applicable.
        if self.state.database:
            self.db_manager = DatabaseManager() 
            if not self.db_manager.open_data(self.state.database):
                raise ValueError(f"Open {self.state.database} error !")            
        # Opening pdn at startup if necessary.
        if self.state.pdn:
            self.pdn_manager = PdnManager() 
            if not self.pdn_manager.open_data(self.state.pdn):
                raise ValueError(f"Open {self.state.pdn} error !")
            
        if self.pdn_manager or self.db_in_read:
            self.state.set_in_viewer(True)
                        
    def _finalize(self):
        """
        Sources closure when exiting match loops with EXIT
        """

        # Database closure
        if self.state.database:
            self.db_manager.close_data()
        # Pdn closure
        if self.state.pdn:
            self.pdn_manager.close_data()

    def match(self):
        """
        Match data management:
         1) with 'view' from PDN examine header data and copy 'pdn_game' to state.
         2) with database writing generate 'pk_game', if not already present, and copy it to state
        """

        if self.pdn_manager:
            if not self.pdn_manager.is_open():
                raise ValueError(f"PdnManager not open or game not present !")
            
            str_match = "Match number " + self.state.pdn_game
            if not self.pdn_manager.game_data(self.state.pdn_game):
                str_match += " not present !"
                self.state.exit = True
            print(str_match)

        if self.db_manager:
            if not self.db_manager.is_open():
                raise ValueError(f"DbManager not open or game not present !")

            self.db_manager.game_data(self.state.pk_game)
            self.state.pk_game = self.db_manager.get_id_game()

    def next_match(self):
        if self.config.execution_mode == EnumExecutionMode.VIEW:
            if self.pdn_manager:
                self.state.pdn_game = self.pdn_manager.next_game()
                
            if self.db_manager:
                self.state.pk_game = self.db_manager.next_game()
        else:
            self.state.pk_game = ""

        self.match()

    def players(self):   
        """
        This method is handled every new game in the checkerboard loop.
        If restore has not been performed:
         1) rebuild pk_players from database if 'view' or from config (randomized) if 'play'.
         2) reset state with pk_players
        Hint: player (engine/name) and pk_game can be changed at the end of each game!        
        """     
        
        data_source : DataInterface | None = self.get_data_source()
        
        if self.restore == None:
            if self.config.execution_mode == EnumExecutionMode.VIEW:
                players : tuple[str,str] = data_source.get_players()
                pk_players : tuple[str,str] = self.state.add_engine_players("player", players)
            elif self.config.execution_mode == EnumExecutionMode.PLAY:
                # Randomly assign colors to players
                pk_players : tuple[str,str] = (self.player_light, self.player_dark)
                # 'random.sample' returns a new sequence with the elements shuffled.
                pk_players = tuple(self.rng.sample(pk_players, k=2))
            else:
                raise ValueError(f"Mode error")
            self.state.reset(pk_players)
        else:
            self.restore = None

        if data_source:
            data_source.set_turn(self.state.number_move, self.state.player_turn)
        self.state.print_playes()

    def get_data_source(self)->DataInterface | None:
        if self.config.execution_mode != EnumExecutionMode.VIEW:
            return None

        # return self.pdn_manager if self.config.import_pdn_name else self.db_manager
        if self.pdn_manager:
            return self.pdn_manager
        return self.db_manager

    def reset_inference_cache(self):
        self._inference_cache.clear()

    def get_inference_source(self)->Optional[InferenceInterface]:
        """
        Inference (dispatcher) if 'classic' or 'ML', but traceable even if 'view'
        """
        inference_key = (
            "view" 
            if self.config.execution_mode == EnumExecutionMode.VIEW
            else self.state.get_engine()
        )

        if inference_key is None:
            return None

        # Hint: if the engine doesn't change during the game, consider caching it 
        # if ML load becomes heavy !
        if inference_key not in self._inference_cache:
            self._inference_cache[inference_key] = InferenceFactory.create_inference(
            inference_key, 
            self.get_data_source()
        )
            
        return self._inference_cache[inference_key]
