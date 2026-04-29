import enum
import random
from typing import Optional
from dataclasses import dataclass
from checkers.config_manager import ConfigManager, EnumExecutionMode
from checkers.engine.game.state import State, EnumResult #, StateMove
from checkers.engine.game.pieces import EnumPlayersColor
from checkers.data.db_manager import DatabaseManager
from checkers.data.pdn_manager import PdnManager
from checkers.data.db_reader import DatabaseReader
from checkers.data.data_interface import DataInterface, SupportsStats
from checkers.engine.inference_interface import InferenceInterface
from checkers.engine.inference_factory import InferenceFactory

# Class used to define the resource type.
# Hint: determines the handling of the id_game : order number, pk !
@enum.unique
class EnumResourceType(enum.Enum):
    R_NONE = 0
    R_DATABASE = 1
    R_PDN = 2

_RESOURCES_MAP = {
    "db" : (DatabaseManager, EnumResourceType.R_DATABASE),
    "pdn": (PdnManager, EnumResourceType.R_PDN)
}    

@dataclass(frozen=True)
class ResourceInfo:
    manager : DataInterface | None = None
    type : EnumResourceType = EnumResourceType.R_NONE
    filename : str = ""
    id_game : str = ""

class Resources:
    """
    Resource class for import/export to database and/or PDN.

    The "import_name/export_name" are optional :
    - "import_name" (.db/.pdn) is required in 'view' mode.
      Using "view" mode requires the availability of a database for reading
      games, which can be created by playing a match with "export_name"
      enabled, or by importing PDN (Portable Drafts Notation) formats.
    - "export_name" (.db/.pdn) is optional and must be enabled to archive games.

    The "restore" option can be applied to "play" and "view" modes. It also works without
    enabling archives through .json files saved in /restores.
    """

    def __init__(self, config:ConfigManager, state:State):
        self.config = config
        self.state = state
        self.import_data : ResourceInfo = ResourceInfo()
        self.export_data : ResourceInfo = ResourceInfo()
        self.restore : Optional[str] = self.config.restore_name
        self.player_light : str = self.state.build_pk_player(self.config.player1_engine, self.config.player1_name)
        self.player_dark  : str = self.state.build_pk_player(self.config.player2_engine, self.config.player2_name)
        # Testable determinism
        self.rng = random.Random(self.config.seed)
        # Inference cache
        self._inference_cache : dict[str, InferenceInterface] = {}

    def __enter__(self):
        self._initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._finalize()

    def _factory_resource(self, name:str)->ResourceInfo:
        try:
            ext : str = name.split('.')[1].lower()
            class_manager, type = _RESOURCES_MAP[ext]

            return ResourceInfo(
                class_manager(),
                type,
                name,
                self.config.import_game
            )
        except IndexError:
            raise KeyError(f"Class Resources, _factory_resource() : unknown resource type !")   

    def _validate_resource(self, import_name : str, import_game :str, export_name : str, restore:str):
        if (
            self.config.execution_mode != EnumExecutionMode.PLAY and 
            self.config.execution_mode != EnumExecutionMode.VIEW
        ):
            raise ValueError(f"Class Resources, _validate_resource() : mode error !")
        
        if self.config.execution_mode == EnumExecutionMode.VIEW:
            if not import_name or not import_game:
                raise ValueError(
                    "Class Resources, _validate_resource() : mode 'view' without 'import_name' or 'import_game' !"
                )
        elif import_name:
            raise ValueError(
                "Class Resources, _validate_resource() : import option not compatible with 'play' mode !"
            )
            
        if (import_name and export_name and import_name == export_name):
            raise ValueError(f"Class Resources, _validate_resource() : import/export resources must be different !")
        
        if not restore:
            self.state.import_name = import_name if import_name is not None else ""
            self.state.import_game = import_game
            self.state.export_name = export_name if export_name is not None else ""
        else:
            if export_name and not self.state.export_game:
                raise ValueError(
                    "Class Resources, _validate_resource() : export without 'export_game' in restore !"
                )
            
    def _initialize(self):
        """
        Resources initialization context : 
         1) if restore is enabled, acquire data in State from /restores, otherwise only the
            import/export name, then save it in State
         2) open import/export classes if present
        """
        
        if self.restore:
            # If restore is enabled, the restart will acquire the data saved in /restores,
            # which partially overwrites the data in the configuration file
            self.state.restore(self.restore)
            self._validate_resource(
                self.state.import_name, self.state.import_game, 
                self.state.export_name, self.restore)
        else: 
            # Getting sources name on startup without restoring   
            # The variables with the names of the db/pdn and identifiers game are kept saved in State
            self._validate_resource(
                self.config.import_name, self.config.import_game, 
                self.config.export_name, self.restore)

        if self.state.import_name:            
            self.import_data = self._factory_resource(self.state.import_name)
            if not self.import_data.manager.open_data(self.state.import_name):
                raise ValueError(f"Class Resources, _initialize() : open {self.state.import_name} error !") 
        if self.state.export_name:            
            self.export_data = self._factory_resource(self.state.export_name)
            if not self.export_data.manager.open_data(self.state.export_name, self.restore):
                raise ValueError(f"Class Resources, _initialize() : open {self.state.export_name} error !") 

    def _finalize(self):
        """
        Sources closure when exiting match loops with EXIT
        """

        # Import closure
        if self.import_data.manager:
            self.import_data.manager.close_data()
            self.import_data = ResourceInfo()

        # Export closure
        if self.export_data.manager:
            self.export_data.manager.close_data()
            self.export_data = ResourceInfo()

    def match(self):
        """
        During import, the presence of the game identified by 'import_game' is checked for the 
        acquisition of game data ('view' mode); if it is not present, a message is displayed.
        During export, the presence of the game identified by 'export_game' is checked to 
        continue with writing the game data; if it is not present, a new game is added.

        Match data management:        
         1) with 'view' from PDN examine header data and copy 'import_game' to state.
         2) with database writing generate 'pk_game', if not already present, and copy it to state
        """

        if self.import_data.manager:
            res : DataInterface = self.import_data.manager
            if not res.is_open():
                raise ValueError(f"Class Resources, match() : import resource not open !")
            
            found : bool = res.game_data(self.state.import_game)

            str_match : str = "Import " + self.import_data.filename + ", "
            match self.import_data.type:
                case EnumResourceType.R_PDN:
                    str_match += "order number = " + self.state.import_game
                    if not found:
                        str_match += " not present !"
                        if self.config.graphics_disabled:
                            self.state.exit = True
                case EnumResourceType.R_DATABASE:
                    if not found:
                        raise ValueError(f"Class Resources, match() : identifier game '{self.state.import_game}' not present !")
                    else:
                        pk = res.get_id_game()
                        str_match += "pk number = " + pk
                        if pk != self.state.import_game:
                            str_match += " (order number = " + self.state.import_game + ")"
            print(str_match)

        if self.export_data.manager:
            res : DataInterface = self.export_data.manager
            if not res.is_open():
                raise ValueError(f"Class Resources, match() : export resource not open !")
            
            found : bool = res.game_data(self.state.export_game)
            if self.state.export_game and not found:
                raise ValueError(f"Class Resources, match() : identifier game '{self.state.export_game}' not present !")

            id_game = res.get_id_game()

            str_match : str = "Export " + self.export_data.filename + ", "
            match self.export_data.type:
                case EnumResourceType.R_PDN:
                    str_match += "order number = " + id_game
                case EnumResourceType.R_DATABASE:
                    str_match += "pk number = " + id_game
            print(str_match)
            self.state.export_game = id_game

    def players(self):   
        """
        This method is handled every new game in the checkerboard loop.
        If restore has not been performed:
         1) rebuild pk_players from database if 'view' or from config (randomized) if 'play'.
         2) reset state with pk_players
        Hint: player (engine/name) and pk_game can be changed at the end of each game!        
        """     
        
        if self.restore == None:
            if self.config.execution_mode == EnumExecutionMode.VIEW:
                items : tuple[str,str,str,str] = self.import_data.manager.get_pk_players()
                pk_players : tuple[str,str] = (
                    self.state.build_pk_player(items[0], items[1]),
                    self.state.build_pk_player(items[2], items[3])
                )
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

        self.persist_game()            
        if self.import_data.manager:
            self.import_data.manager.set_turn(self.state.number_move, self.state.player_turn)
        self.state.print_match()

    def next_match(self):
        if self.import_data.manager:
            self.state.import_game = self.import_data.manager.next_game(not self.config.graphics_disabled)
        self.state.export_game = ""
        self.match()

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
            self.import_data.manager
        )
            
        return self._inference_cache[inference_key]
    
    def persist_game(self):
        if self.export_data.manager:
            self.export_data.manager.write_game(self.state.export_game, self.state.pk_players_as_tuple())
                
    def persist_turn(self):
        if self.export_data.manager:
            self.export_data.manager.write_move(
                self.state.number_move, self.state.player_turn, self.state.last_state_move,
                self.state.get_dark_cells_state())
            
        DatabaseReader.print_state(self.state.get_dark_cells_state())

    def persist_result(self):
        if self.export_data.manager:
            self.export_data.manager.write_result(self.state.result)
            
    def persist_stats(self):
        match self.state.result:
            case EnumResult.R_LIGHT:
                stats = ((1,0,0), (0,0,1))
            case EnumResult.R_PARITY:
                stats = ((0,1,0), (0,1,0))
            case EnumResult.R_DARK:
                stats = ((0,0,1), (1,0,0))
            case _:
                stats = ((0,0,0), (0,0,0))

        for player in EnumPlayersColor:
            self.state.data_players[player].add_local_history(stats[player.value])
            manager: DataInterface = self.export_data.manager
            if isinstance(manager, SupportsStats):
                manager.add_stats_player(player, stats[player.value])

    def db_reader(self):
        exit : bool = False
        while not exit:
            with DatabaseReader() as db_reader: 
                db_reader.extract_information()
                exit = db_reader.interactive_console()
