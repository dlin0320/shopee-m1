import sqlite3

class Advertisement:
    def __init__(self, dir) -> None:
        self.conn = sqlite3.connect(f'{dir}/local.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            DROP TABLE IF EXISTS advertisements
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS advertisements(
                shop TEXT,
                id TEXT,
                name TEXT,
                price TEXT,
                PRIMARY KEY (id, name)
            )
        ''')
        self.conn.commit()
    
    def insert(self, item):
        self.cursor.execute('''
            INSERT OR IGNORE INTO advertisements VALUES (?,?,?,?)
        ''', item)
        self.conn.commit()

    def select(self, name=None):
        if name == None:
            self.cursor.execute('''
                SELECT * FROM advertisements
            ''')
        else:
            self.cursor.execute(f'SELECT * FROM advertisements WHERE name=\'{name}\'')
        return self.cursor.fetchall()

class History:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('local.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS histories(
                shop TEXT,
                id TEXT,
                name TEXT,
                price TEXT,
                target TEXT,
                PRIMARY KEY (id, name)
            )
        ''')

    def insert(self, item):
        self.cursor.execute('''
            INSERT OR IGNORE INTO histories VALUES (?,?,?,?,?)
        ''', item)
        self.conn.commit()

    def update(self, target, id, name):
        self.cursor.execute(f'UPDATE histories SET target=\'{target}\' WHERE id= \'{id}\' AND name=\'{name}\'')
        self.conn.commit()
    
    def delete(self, id, name):
        self.cursor.execute(f'DELETE FROM histories WHERE id= \'{id}\' AND name=\'{name}\'')
        self.conn.commit()

    def select(self, id=None, name=None):
        if id == None and name == None:
            self.cursor.execute('''
                SELECT * FROM histories
            ''')
        else:
            self.cursor.execute(f'SELECT * FROM histories WHERE id = \'{id}\' AND name=\'{name}\'')
        return self.cursor.fetchall()