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
    """

    def __init__(self, config:ConfigManager, state:State):
        self.config = config
        self.state = state
        self.db_manager: DataInterface | None = None
        self.pdn_manager: DataInterface | None = None        
        self.restore : Optional[str] = self.config.restore_name
        self.player_light : str = self.state.build_pk_player(self.config.player1_engine, self.config.player1_name)
        self.player_dark  : str = self.state.build_pk_player(self.config.player2_engine, self.config.player2_name)
        self.pk_game : Optional[str] = self.config.pk_game
        # Testable determinism
        self.rng = random.Random(self.config.seed)
        # Inference cache
        self._inference_cache : dict[str, InferenceInterface] = {}

    def is_empty(value:Optional[str])->bool: 
        return value is None or value == ""
        # return not value # with intrinsic falsity
    
    def initialize(self):
        # Hint: different from empty string only in 'play' with history active or in 'view'!
        database : str = ""
        pdn : str = ""

        # If restore is enabled, the restart will acquire the data saved in /restores,
        # which partially overwrites the data in the configuration file
        if self.restore != None:
            self.state.restore(self.restore)
        else: 
            # Getting database name on startup without restoring   
            if (
                self.config.execution_mode != EnumExecutionMode.PLAY and 
                self.config.execution_mode != EnumExecutionMode.VIEW
            ):
                raise ValueError(f"Mode error !")
            
            if ( 
                self.config.execution_mode == EnumExecutionMode.VIEW and 
                self.is_empty(self.config.history_db_name) and 
                self.is_empty(self.config.import_pdn_name)
            ): 
                raise ValueError("Mode 'view' without resource: 'history_database'/'import_pdn'!")
            
            if not self.is_empty(self.config.history_db_name):
                database = self.config.history_db_name
            if not self.is_empty(self.config.import_pdn_name):
                pdn = self.config.import_pdn_name
            # The variable with the name of the database/pdn is kept saved in State
            self.state.database = database
            self.state.pdn = pdn
                
        # Opening database at startup, if applicable.
        if self.state.database:
            self.db_manager = DatabaseManager(self.config) 
            if self.db_manager.open_data(self.state.database):
                raise ValueError(f"Open {self.state.database} error !")
        # Opening pdn at startup if necessary.
        if self.state.pdn:
            self.pdn_manager = PdnManager(self.config) 
            if self.pdn_manager.open_data(self.state.pdn):
                raise ValueError(f"Open {self.state.pdn} error !")
            
    def finalize(self):
        # Database closure
        if self.state.database:
            self.db_manager.close_data()
        # Pdn closure
        if self.state.pdn:
            self.pdn_manager.close_data()

    def reset_inference_cache(self):
        self._inference_cache.clear()

    # Hint: This method is handled every new game in the checkerboard loop.
    # Only player1/2_engine/name and pk_game can be changed.
    def assign_player_and_color(self):        
        if self.restore == None:
            if self.config.execution_mode == EnumExecutionMode.VIEW:
                data_source : DataInterface = self.get_data_source()
                pk_players : tuple[str,str] = data_source.get_players(self.pk_game)
            elif self.config.execution_mode == EnumExecutionMode.PLAY:
                self.pk_game = self.state.generate_pk_game()
                # Randomly assign colors to players
                pk_players : tuple[str,str] = (self.player_light, self.player_dark)
                # 'random.sample' returns a new sequence with the elements shuffled.
                pk_players = tuple(self.rng.sample(pk_players, k=2))
            else:
                raise ValueError(f"Mode error")        
            self.state.reset(self.pk_game, pk_players)
        else:
            self.restore = None

    def get_data_source(self)->DataInterface:
        # return self.pdn_manager if self.config.import_pdn_name else self.db_manager
        if self.pdn_manager:
            return self.pdn_manager
        return self.db_manager

    def get_inference_source(self)->Optional[InferenceInterface]:
        inference_key = (
            "view" 
            if self.config.execution_mode == EnumExecutionMode.VIEW
            else self.state.get_engine()
        )

        if inference_key is None:
            return None

        # inference (dispatcher) if 'classic' or 'ML', but traceable even if 'view'
        # Hint: if the engine doesn't change during the game, consider caching it 
        # if ML load becomes heavy : 'if engine != self._last_engine:' !
        if inference_key not in self._inference_cache:
            self._inference_cache[inference_key] = InferenceFactory.create_inference(
            inference_key, 
            self.get_data_source()
        )
            
        return self._inference_cache[inference_key]
