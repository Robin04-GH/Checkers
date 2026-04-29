import os
from datetime import datetime, timezone
from dataclasses import dataclass
from checkers.constant import PATH_LOG
from checkers.data.db_manager import DatabaseManager

@dataclass
class ForeignKeyInfo:
    col_from: str
    table_to: str
    col_to: str

@dataclass
class ForeignKeyIndexed:
    col_from: int
    table_to: int
    col_to: int

class DatabaseReader(DatabaseManager):
    """
    Class for reading database data through an iterative console 
    that automatically generates queries
    """
    
    def __init__(self):
        super().__init__()
        self._db_name : str = ""
        # List of table names (implicit table index)
        self._tables : list[str] = []
        # List of column names grouped by table (implicit table/column indexes)
        self._columns : list[list[str]] = []
        # List of foreign keys grouped by from table (implicit table/fk indexes):
        # (from table column, to table column, to table column)        
        self._indexed_foreigns : list[list[ForeignKeyIndexed]] = []
        # Query main table index
        self._main_table : int = -1

        # Table index dictionary to speed up assignment 'self._indexed_foreigns'        
        self._table_index : dict[str, int] = {}
        # Dictionary column indexes to speed up assignment 'self._indexed_foreigns'
        self._column_index : dict[str, dict[str, int]] = {}
        # Temporary dictionary for table prefix counting
        self._cnt_prefix : dict[str, int] = {}
        # Dictionary with unique table prefix key to speed up 'join_prefix_to_table_to()'
        self._prefix_to_table : dict[str, int] = {}
                
        # List of unique prefixes for tables in the presence of joins: initial letter + number
        self._table_prefix : list[str] = []
        # List of full fk prefixes for the subset of joins used in the query:
        # key = (from table, fk index relative to the table) : value = full prefix
        # Hint: the full prefix is ​​constructed from the unique prefix of the 'to table' with
        # the addition of an '_n' only if there are multiple fk indexes on the from table.
        # (with n being the fk index relative to the from table in the subset of joins used 
        # in the query)
        self._join_prefix : dict[tuple[int, int], str] = {}

        self._select : str = ""
        self._join : list[str] = []
        self._where : str = ""
        self._sorting : str = ""
        self._output : int = 0

    def __enter__(self):
        print(f"\nDatabase Reader")
        print(f"Interactive Console")
        self._db_name : str = input(f"Database name ? ")
        self.open_data(self._db_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_data()

    def build_prefix(self, table_name:str)->str:
        initial : str = table_name[0]
        if initial in self._cnt_prefix.keys():
            self._cnt_prefix[initial] += 1
        else:
            self._cnt_prefix[initial] = 0

        prefix : str = f"{initial}{self._cnt_prefix[initial]}"
        return prefix
    
    def build_suffix(self, t:tuple[int, int])->str:
        suffix : str = ""
        index_table_from, index_fk = t
        
        if index_table_from >= len(self._tables):
            raise ValueError(f"Class DatabaseReader, build_suffix() : index table error !")
        
        items = len(self._indexed_foreigns[index_table_from])
        if index_fk >= items:
            raise ValueError(f"Class DatabaseReader, build_suffix() : index foreign key error !")

        if items > 1:
            suffix = f"_{index_fk}"

        return suffix

    def join_prefix_to_table_to(self, join_prefix:str)->int:
        # Extract only the part before the possible "_n" suffix
        # Hint: this works even if the prefixes get longer !
        prefix_table_to = join_prefix.split("_")[0]
        try:
            return self._prefix_to_table[prefix_table_to]
        except KeyError:
            raise ValueError(f"Class DatabaseReader, reverse_join_prefix() : prefix not found !")

    def extract_information(self):
        # Get all table names
        self._cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self._cursor.fetchall()

        literaled_foreigns : list[list[ForeignKeyInfo]] = []
        for table in tables:
            table_name : str = table[0]

            self._load_tables(table_name)
            self._load_columns(table_name)    
            literaled_foreigns.append(self._load_foreign_keys(table_name))

        self._index_foreign_keys(literaled_foreigns)  

    def _load_tables(self, table_name:str):
        print(f"\n Table analysis : {table_name}")
        size : int = len(self._tables)
        self._table_index[table_name] = size
        prefix : str = self.build_prefix(table_name)
        self._table_prefix.append(prefix)
        self._prefix_to_table[prefix] = size
        self._tables.append(table_name)

    def _load_columns(self, table_name:str):
        tmp_col : list[str] = []
        tmp_idx : dict[str, int] = {}

        # Get details about columns and foreign keys
        self._cursor.execute(f"PRAGMA table_info({table_name});")
        columns = self._cursor.fetchall()

        # Column display
        for idx, col in enumerate(columns):
            # col is a tuple : (cid, name, type, notnull, dflt_value, pk)
            pk = " (PK)" if col[5] else ""
            col_name = col[1]
            print(f"  - {col_name} ({col[2]}){pk}")
            tmp_col.append(col_name)
            tmp_idx[col_name] = idx

        self._columns.append(tmp_col)
        self._column_index[table_name] = tmp_idx

    def _load_foreign_keys(self, table_name:str)->list[ForeignKeyInfo]:
        tmp_fks : list[ForeignKeyInfo] = []

        # Get Foreign Keys
        self._cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        extern_keys = self._cursor.fetchall()

        # Displaying foreign keys
        if extern_keys:
            print(f"  Extern Keys ({len(extern_keys)}):")
            for fk in extern_keys:
                # fk is a tuple : (id, seq, table, from, to, on_update, on_delete, match)
                print(f"   - {fk[3]} ->{fk[4]} (Table: {fk[2]})")
                tmp_fks.append(ForeignKeyInfo(fk[3], fk[2], fk[4]))
        else:
            print("  No foreign key defined")

        return tmp_fks

    # indexed foreigns
    def _index_foreign_keys(self, literaled_foreigns:list[list[ForeignKeyInfo]]):
        # Hint: the index of the tuple list is used as an additional suffix for joined columns !
        for idx_table_from, fks in enumerate(literaled_foreigns):
            tmp_t : list[ForeignKeyIndexed] = []
            for fk in fks:
                idx_table_to : int = self._table_index[fk.table_to]
                tmp_t.append(
                    ForeignKeyIndexed
                    (
                        self._column_index[self._tables[idx_table_from]][fk.col_from],
                        idx_table_to,
                        self._column_index[self._tables[idx_table_to]][fk.col_to]
                    ) 
                )
            self._indexed_foreigns.append(tmp_t)   

    # Method for inputting column indices:
    # - prompt: descriptive string
    # - start, end: lower and upper bounds (both within the valid range),
    # possibly unspecified
    # - multi: if True, enables input of multiple indices separated by ','
    # - nothing: if True, enables the option to not edit any indices
    # - sign: if True, allows editing of signed indices (> 0 for ASC, < 0 for DESC),
    # used only for ORDER BY
    def index_editor(
        self, 
        prompt:str, 
        start:int | None, 
        end:int | None,
        multi:bool = False,
        nothing:bool = False, 
        sign:bool = False
    )->tuple[int, ...]:

        tmp_idx : list[int] = []
        all_value = end + 1 if multi else None

        # Dynamic message
        mode_input = "multi" if multi else "single"
        mode_empty = "allowed" if nothing else "not allowed"
        mode_sign = "allowed" if sign else "not allowed"

        print(f"Valid range: {start}-{end}, input {mode_input}, empty {mode_empty}, sign {mode_sign}", end="")
        if multi:
            print(f", '{all_value}' = all")
        else:
            print()

        while True:
            tmp_idx.clear()
            raw = input(prompt).strip()

            # Robust normalization
            parts = [p.replace(" ", "") for p in raw.split(',') if p.strip()]

            # Preliminary checks
            if not parts and not nothing:
                print("Set at least one index!")
                continue

            if len(parts) > 1 and not multi:
                print("Incorrect input: only one index allowed!")
                continue

            valid = True
            for p in parts:

                # Sign Management
                negative = False
                if sign and p.startswith('-'):
                    negative = True
                    p = p[1:]

                # Robust conversion
                try:
                    idx = int(p)
                except ValueError:
                    print(f"Incorrect input: {p} is not a number!")
                    valid = False
                    break

                # Shortcut "all"
                if multi and idx == all_value:
                    tmp_idx = [i if not negative else -i for i in range(start, all_value)]
                    break

                # Range check
                if (start is not None and idx < start) or (end is not None and idx > end):
                    print(f"Incorrect input: {idx} out of range [{start},{end}]!")
                    valid = False
                    break

                tmp_idx.append(idx if not negative else -idx)

            if valid:
                return tuple(tmp_idx)
            
    def main_table_select(self)->int:
        print(f"\nMain table selection :")
        for index, table in enumerate(self._tables):
            print(f" {index+1} - {table}")
        index_table = self.index_editor("Choose ? ", 1, len(self._tables))[0]

        return index_table - 1
        
    def join_select(self)->list[str]:
        ret_list : list[str] = []
        print(f"\nJoin selection :")

        tmp_list : list[tuple[int, int]] = []
        counter = 1

        # Clear enumeration of FKs
        for idx_table, fks in enumerate(self._indexed_foreigns):
            for idx_fk, fki in enumerate(fks):
                col_from = self._columns[idx_table][fki.col_from]
                table_from = self._tables[idx_table]
                col_to = self._columns[fki.table_to][fki.col_to]
                table_to = self._tables[fki.table_to]

                print(f" {counter} - {table_from}.{col_from} -> {table_to}.{col_to}")
                tmp_list.append((idx_table, idx_fk))
                counter += 1

        # Input
        t_edit = self.index_editor(
            "Select joins (comma separated) ? ",
            1,
            counter - 1,
            multi=True,
            nothing=True
        )

        if len(t_edit) == 0:
            self._join_prefix.clear()
            return ret_list

        # Join construction
        for idx_edit in t_edit:
            idx = idx_edit - 1
            idx_table_from, idx_fk = tmp_list[idx]
            fki = self._indexed_foreigns[idx_table_from][idx_fk]

            key = (idx_table_from, idx_fk)
            prefix_to = self._table_prefix[fki.table_to] + self.build_suffix(key)
            self._join_prefix[key] = prefix_to

            join_str = (
                f"{self._tables[fki.table_to]} {prefix_to} ON "
                f"{self._table_prefix[idx_table_from]}.{self._columns[idx_table_from][fki.col_from]} = "
                f"{prefix_to}.{self._columns[fki.table_to][fki.col_to]}"
            )
            ret_list.append(join_str)

        return ret_list

    def print_columns_table(self, idx_table:int)->int:
        items = len(self._columns[idx_table])
        for index, column in enumerate(self._columns[idx_table], start = 1):
            print(f" {index} - {column}")
        return items

    def columns_choose(self, multi=False, nothing=False, sign=False)->dict[str, tuple[int, ...]]:
        while True:
            columns : dict[str, tuple[int, ...]] = {}

            # 1) Main table
            idx_table = self._main_table
            prefix = self._table_prefix[idx_table]

            print(f"\nMain Table ({self._tables[idx_table]}) :")
            items = self.print_columns_table(idx_table)

            t = self.index_editor("Choose column(s) ? ", 1, items, multi, True, sign)
            if len(t) > 0:
                columns[prefix] = t

            # 2) Tables joined via JOIN
            for (table_from, idx_fk), join_prefix in self._join_prefix.items():
                # Intermediate single-mode check to prevent edits on linked tables when
                # the column has already been set in previous tables
                if not multi and len(columns) > 0:
                    break

                fki = self._indexed_foreigns[table_from][idx_fk]
                idx_table = fki.table_to

                print(f"\nFK {self._columns[table_from][fki.col_from]} ({self._tables[table_from]}) → "
                    f"{self._columns[fki.table_to][fki.col_to]} ({self._tables[fki.table_to]}) :")

                items = self.print_columns_table(idx_table)
                t = self.index_editor("Choose column(s) ? ", 1, items, multi, True, sign)
                if len(t) > 0:
                    columns[join_prefix] = t

            # Final check
            if nothing or len(columns) > 0:
                return columns

            print("You need to set at least one column!")

    def columns_select(self)->str:
        print(f"\n[ SELECT columns ]")
        columns = self.columns_choose(True, True)

        parts = []
        for prefix, list_col in columns.items():
            table_to = self.join_prefix_to_table_to(prefix)
            p = f"{prefix}." if len(self._join_prefix) > 0 else ""
            for col in list_col:
                parts.append(f"   {p}{self._columns[table_to][col-1]}")

        return ",\n".join(parts)

    def columns_where(self)->str:
        print(f"\n[ WHERE column ]")

        parts = []
        first = True
        items = 1

        while True:
            if first:
                print("\nAdd filters with WHERE expressions (0=No, 1=Yes) :")
            else:
                print("\nAdd more where expressions :")
                print(" 0 - No")
                print(" 1 - AND")
                print(" 2 - OR")
                items = 2

            add_expr = self.index_editor("Choose ? ", 0, items)[0]
            if add_expr < 1:
                break

            column = self.columns_choose()
            expression = input("\nWrite expression : ")

            logic = ""
            if not first:
                logic = "AND" if add_expr == 1 else "OR"

            for prefix, list_col in column.items():
                table_to = self.join_prefix_to_table_to(prefix)
                p = f"{prefix}." if len(self._join_prefix) > 0 else ""
                for col in list_col:
                    parts.append(f"{logic} {p}{self._columns[table_to][col-1]} {expression}".strip())

            first = False

        return " ".join(parts)

    def columns_order(self)->str:
        print(f"\n[ ORDER BY columns ]")
        columns = self.columns_choose(True, True, True)

        parts = []
        for prefix, list_col in columns.items():
            table_to = self.join_prefix_to_table_to(prefix)
            p = f"{prefix}." if len(self._join_prefix) > 0 else ""
            for col in list_col:
                order = "ASC" if col > 0 else "DESC"
                parts.append(f"{p}{self._columns[table_to][abs(col)-1]} {order}")

        sorting_string = ", ".join(parts)

        print("\nLimit number of lines displayed, 0 = Not limit : ")
        limit = self.index_editor("Choose ? ", 0, None)[0]
        if limit >= 1:
            sorting_string += f" LIMIT {limit}"

        return sorting_string

    def choose_output(self)->int:
        outp = 0
        print(f"\nOutput :")
        print(f" 1 - console")
        print(f" 2 - query_xxx.txt")
        print(f" 3 - both")

        outp = self.index_editor("Choose ? ", 1, 3)[0]
        
        return outp

    def interactive_console(self)->bool:
        while True:
            if self._main_table < 0:
                self._main_table = self.main_table_select()

            self._join = self.join_select()
            self._select = self.columns_select()
            self._where = self.columns_where()
            self._sorting = self.columns_order()
            self._output = self.choose_output()

            self.print_result()

            print("\nNext iteration :")
            print(" 0 - exit")
            print(" 1 - new database")
            print(" 2 - new main table")
            print(" 3 - new query")

            next = self.index_editor("Choose ? ", 0, 3)[0]

            if next == 0:
                return True
            if next == 1:
                return False
            if next == 2:
                self._main_table = -1
            if next == 3:
                pass  # repeats with same table
             
    def build_query(self)->str:
        alias = self._table_prefix[self._main_table] if self._join_prefix else ""
        query = f"SELECT\n{self._select}\nFROM {self._tables[self._main_table]} {alias}"

        for join in self._join:
            query += f"\nJOIN {join}"

        if self._where:
            query += f"\nWHERE {self._where}"

        if self._sorting:
            query += f"\nORDER BY {self._sorting}"

        return query + ";"
   
    def print_result(self):
        query = self.build_query()

        results = [f'\n"""\n{query}\n"""\n\n']
        try:
            for row in self._cursor.execute(query):
                results.append(f"{row}\n")
        except Exception as e:
            print(f"\nClass DatabaseReader, print_result() : query error {e}\n")
            print(f"Failed query:\n{query}")
            return            

        # Output console
        if self._output & 1:
            for row in results:
                print(row, end = "")

        # Output file
        if self._output & 2:
            if not os.path.isdir(PATH_LOG):
                raise ValueError(f"Database path does not exist : {PATH_LOG}")   
             
            self._name_log = "query_" + datetime.now(timezone.utc).strftime("%d%H%M%S") + ".txt"
            filepath = os.path.join(PATH_LOG, self._name_log)

            with open(filepath, "w") as f:
                f.write(f"Database = {self._db_name}\n")
                f.writelines(results)

    @staticmethod
    def print_state(checkerboard:list[int]):
        if checkerboard is None:
            return

        if len(checkerboard) != 32:
            print("Class DatabaseManager, print_state() : invalid checkerboard length !")
            return

        for index, dark_cell in enumerate(checkerboard):
            row = index // 4
            light_cell = 0
            if row % 2 == 0:
                print(f"{dark_cell:3d}, {light_cell:3d},", end=" ")
            else:
                print(f"{light_cell:3d}, {dark_cell:3d},", end=" ")

            if index % 4 == 3:
                print()
