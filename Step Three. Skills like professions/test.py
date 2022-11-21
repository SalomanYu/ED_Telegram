from config import MYSQL
from database import connect_to_db


con = connect_to_db()
with con.cursor() as cursor:
    cursor.execute(f"SELECT * FROM {MYSQL.TABLE.value} WHERE value='ccs3'")
    print(cursor.fechall())
    con.close()