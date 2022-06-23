import os
import sqlite3

from .settings import Connection, RowData


def connect_to_db(name) -> Connection:
    os.makedirs(name='SQL', exist_ok=True)
    db = sqlite3.connect(f'SQL/{name}.db')
    cursor = db.cursor()

    return cursor, db

def create_table(table_name:str, db_name:str) -> None:
    cursor, db = connect_to_db(db_name)

    pattern = f"""
        CREATE TABLE IF NOT EXISTS {table_name}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_num INTEGER, 
            old_name VARCHAR(255),
            new_name VARCHAR(255)
        )
    """
    cursor.execute(pattern)
    db.commit()
    db.close()

def add(db_name:str, table_name:str, data:RowData) -> None:
    print(data)
    cursor, db = connect_to_db(db_name)

    pattern = f"""
        INSERT INTO {table_name}(
            id_num,
            old_name,
            new_name
        ) VALUES({','.join('?' for i in range(len(data)))})
    """
    cursor.execute(pattern, data)
    db.commit()
    db.close()

if __name__ == "__main__":
    create_table('test', 'hello')
    add(db_name='hello', table_name='test', data=('Hello World', 'world', 'hello', False))