import pymysql
from pymysql.connections import Connection

from config import Skill, MYSQL


def connect_to_db() -> Connection:
    try:
        connection = pymysql.connect(
                host=MYSQL.HOST.value,
                port=MYSQL.PORT.value,
                database=MYSQL.DB.value,
                user=MYSQL.USER.value,
                password=MYSQL.PASSWORD.value,
                cursorclass=pymysql.cursors.DictCursor
            )
        print("Success connection to db..")
        return connection

    except Exception as ex:
        exit(f"Error by connection: {ex}")


def get_skill_from_database() -> Skill:
    """Возвращает самую первую пару навыков, у которой значение is_duplicate является None. 
    Таким образом, мы понимаем, что с этой парой еще не работали"""
    
    connection = connect_to_db()
    with connection.cursor() as cursor:
        query_get_null_couple = f"SELECT * FROM {MYSQL.TABLE.value}  WHERE is_displayed IS NULL LIMIT 1"

        cursor.execute(query_get_null_couple)
        skill = cursor.fetchone()
        connection.close()
        if skill:return Skill(iD=skill['id'], title=skill['name'], is_dislayed=skill['is_displayed'])
        else:return

def confirm_skill(id: int, confirm: bool = True) -> None:
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            if confirm:
                cursor.execute(f"UPDATE {MYSQL.TABLE.value} SET is_displayed=1 WHERE id={id}")
            else:
                cursor.execute(f"UPDATE {MYSQL.TABLE.value} SET is_displayed=0 WHERE id={id}")

            connection.commit()
    finally:
        connection.close()


def refute_skill(id: int) -> None: # Опровергнуть сходство
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {MYSQL.TABLE.value} SET is_displayed=null WHERE id={id}")
            connection.commit()
            print("Опровергли")

    finally:
        connection.close()

def get_last_viewed_skill() -> Skill | None:
    connection = connect_to_db()
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT * FROM {MYSQL.TABLE.value} WHERE is_displayed IS NOT NULL""")
        skill = cursor.fetchall()[-1]

        try:res = Skill(iD=skill['id'], title=skill['name'], is_dislayed=skill['is_displayed'])
        except: res = None 
        connection.close()

        if res is None: return
        refute_skill(id=res.iD) # Делаем это для того, чтобы мы могли несколько раз подряд нажимать кнопку назад 
        return res


if __name__ == "__main__":
    print(get_skill_from_database())
