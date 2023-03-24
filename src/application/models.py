import sqlite3

class DB(object):
    dir = None

    def __init__(self, dir, command) -> None:
        DB.dir = dir
        _, cursor = DB.connect()
        cursor.execute(command)

    @staticmethod
    def connect():
        conn = sqlite3.connect(f'{DB.dir}/local.db')
        return conn, conn.cursor()

class History(DB):
    def __init__(self, dir) -> None:
        super().__init__(dir, '''
            CREATE TABLE IF NOT EXISTS histories(
                shop TEXT,
                id TEXT,
                name TEXT,
                price TEXT,
                target TEXT,
                PRIMARY KEY (id, name)
            )
        ''')

    @staticmethod
    def insert(item):
        conn, cursor = DB.connect()
        cursor.execute('''
            INSERT OR REPLACE INTO histories VALUES (?,?,?,?,?)
        ''', item)
        conn.commit()

    @staticmethod
    def update(target, id, name):
        conn, cursor = DB.connect()
        cursor.execute(f'UPDATE histories SET target=\'{target}\' WHERE id= \'{id}\' AND name=\'{name}\'')
        conn.commit()
    
    @staticmethod
    def delete(id, name):
        conn, cursor = DB.connect()
        cursor.execute(f'DELETE FROM histories WHERE id= \'{id}\' AND name=\'{name}\'')
        conn.commit()

    @staticmethod
    def select(id=None, name=None):
        _, cursor = DB.connect()
        if id == None and name == None:
            cursor.execute('SELECT * FROM histories')
        else:
            cursor.execute(f'SELECT * FROM histories WHERE id = \'{id}\' AND name=\'{name}\'')
        res = cursor.fetchall()
        return res

class Shop(DB):
    def __init__(self, dir) -> None:
        super().__init__(dir, '''
            CREATE TABLE IF NOT EXISTS shops(
                id TEXT,
                cookie TEXT,
                agent TEXT,
                PRIMARY KEY (id)
            )
        ''')

    @staticmethod
    def insert(item):
        conn, cursor = DB.connect()
        cursor.execute('''
            INSERT OR REPLACE INTO shops VALUES (?,?,?)
        ''', item)
        conn.commit()

    @staticmethod
    def select():
        _, cursor = DB.connect()
        cursor.execute(f'SELECT * FROM shops')
        res = cursor.fetchall()
        return res