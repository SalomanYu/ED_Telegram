import sqlite3

from config import Skill


def connect_to_db(db_name: str = "skills.db") -> Skill | None:
    db = sqlite3.connect(db_name)
    return  db, db.cursor()

def get_not_viewed_skill():
    db, cursor = connect_to_db()
    cursor.execute("SELECT * FROM skill WHERE confirm IS NULL LIMIT 1")
    result = cursor.fetchone()
    
    db.close() 
    if result:return Skill(*result)
    else: return 

def confirm_profession(skill_id: int) -> None:
    db, cursor = connect_to_db()
    cursor.execute(f"UPDATE skill SET is_profession=true WHERE id={skill_id}")
    db.commit()
    db.close()

def set_confirm_skill(skill_id: int, confirm: bool = True) -> None:
    db, cursor = connect_to_db()
    if confirm:
        cursor.execute(f"UPDATE skill SET confirm=1 WHERE id={skill_id}")
    else:
        cursor.execute(f"UPDATE skill SET confirm=0 WHERE id={skill_id}")
    db.commit()
    db.close()
    

def zeroize_table():
    db, cursor = connect_to_db()
    cursor.execute("UPDATE skill SET confirm = NULL, is_profession=false WHERE confirm NOT NULL")
    db.commit()
    db.close()

def get_all_professions() -> tuple:
    db, cursor = connect_to_db()
    cursor.execute("SELECT title FROM skill WHERE is_profession=true")
    return cursor.fetchall()


if __name__ == "__main__":
    zeroize_table()