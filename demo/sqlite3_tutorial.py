"""
SQLite3 
Tutorial da db_manager.py 
"""

def tutorial_create_movie(self):
    self._cursor.execute("CREATE TABLE movie(title, year, score)")

def tutorial_verify_movie(self):
    res = self._cursor.execute("SELECT name FROM sqlite_master")
    print(f"sqlite_master (name) = {res.fetchone()}")
    res = self._cursor.execute("SELECT name FROM sqlite_master WHERE name='spam'")
    print(f"sqlite_master (spam) = {res.fetchone()}")

def tutorial_insert_movie(self):
    self._cursor.execute("""
        INSERT INTO movie VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)
    """)
    self._connection.commit()

def tutorial_verify_insert(self):
    res = self._cursor.execute("SELECT score FROM movie")
    print(f"sqlite_master (score) = {res.fetchall()}")

def tutorial_insert_many_movie(self):
    data = [
        ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
        ("Monty Python's The Meaning of Life", 1983, 7.5),
        ("Monty Python's Life of Brian", 1979, 8.0),
    ]
    self._cursor.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
    self._connection.commit()  # Remember to commit the transaction after executing INSERT.

def tutorial_verify_data(self):
    for row in self._cursor.execute("SELECT year, title FROM movie ORDER BY year"):
        print(row)

def tutorial_verify_highest(self):
    new_cur = self._connection.cursor()
    res = new_cur.execute("SELECT title, year FROM movie ORDER BY score DESC")
    title, year = res.fetchone()
    print(f'The highest scoring Monty Python movie is {title!r}, released in {year}')