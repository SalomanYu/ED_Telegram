import pymysql
from pymysql.connections import Connection

from tools.settings import MYSQL, SimilarCouple


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


def get_couple_skills_from_database() -> SimilarCouple:
    """Возвращает самую первую пару навыков, у которой значение is_duplicate является None. 
    Таким образом, мы понимаем, что с этой парой еще не работали"""
    
    connection = connect_to_db()
    with connection.cursor() as cursor:
        query_get_null_couple = f"SELECT * FROM {MYSQL.TABLE.value}  WHERE is_duplicate IS NULL LIMIT 1"

        cursor.execute(query_get_null_couple)
        first_couple = cursor.fetchone()
        connection.close()
        if first_couple:return SimilarCouple(*first_couple.values())
        else:return

def confirm_similarity(couple_id: int, confirm: bool = True) -> None:
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            if confirm:
                cursor.execute(f"UPDATE {MYSQL.TABLE.value} SET is_duplicate=1 WHERE id={couple_id}")
            else:
                cursor.execute(f"UPDATE {MYSQL.TABLE.value} SET is_duplicate=0 WHERE id={couple_id}")

            connection.commit()
    finally:
        connection.close()


def refute_similarity(couple_id: int) -> None: # Опровергнуть сходство
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {MYSQL.TABLE.value} SET is_duplicate=null WHERE id={couple_id}")
            connection.commit()

    finally:
        connection.close()

def get_last_viewed_skill() -> SimilarCouple | None:
    connection = connect_to_db()
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT * FROM {MYSQL.TABLE.value} WHERE is_duplicate IS NOT NULL""")
        try:res = SimilarCouple(*cursor.fetchall()[-1].values())
        except: res = None
        connection.close()

        if res is None: return
        refute_similarity(couple_id=res.id) # Делаем это для того, чтобы мы могли несколько раз подряд нажимать кнопку назад 
        return res
    


if __name__ == "__main__":
    # skills = get_skills_fromDB()
    couple = get_couple_skills_from_database()
    