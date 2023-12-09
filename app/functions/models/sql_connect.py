from mysql.connector import connect, Error
from app.config import Configs


def sql_search(table: str, columns: str = "*", where: str = None, where_value=None, fetch: str = "one",
               order_by: str = None, order_method: str = None, like: bool = False):
    try:
        with connect(host=Configs.host, database=Configs.database, user=Configs.user,
                     password=Configs.password, use_pure=True) as conn:
            cursor = conn.cursor(named_tuple=True)
            query = f'SELECT {columns} FROM {table}'
            if where:
                if like:
                    query += f" WHERE {where} LIKE {where_value}"
                else:
                    query += f" WHERE {where} = {where_value}"
                # print(query)
                cursor.execute(query)
            else:
                if order_by:
                    query += f' ORDER BY {order_by} {order_method}'
                # print(query)
                cursor.execute(query)
            if fetch == 'all':
                result = cursor.fetchall()
                return result
            elif columns == "*":
                result = cursor.fetchone()
                return result
            else:
                result = cursor.fetchone()
                if result is None:
                    return False
                else:
                    return result[0]
    except Error as e:
        print(f"Error: {e}")
    return False


def sql_insert(table: str, thing: str, value: str):
    try:
        with connect(host=Configs.host, database=Configs.database, user=Configs.user,
                     password=Configs.password, use_pure=True) as conn:
            cursor = conn.cursor()
            query = f'INSERT INTO {table} ({thing}) VALUES ({value})'
            cursor.execute(query)
            conn.commit()

            return True
    except Error as e:
        print(f"Error: {e}")
    return False


def sql_update(table: str, columns: str, value, where: str, where_value):
    try:
        with connect(host=Configs.host, database=Configs.database, user=Configs.user,
                     password=Configs.password, use_pure=True) as conn:
            cursor = conn.cursor()
            query = f'UPDATE {table} SET {columns} = {value} WHERE {where} = {where_value}'
            # print(query)
            cursor.execute(query)
            conn.commit()
            return True
    except Error as e:
        print(f"Error: {e}")
    return False


def sql_delete(table: str, where: str, where_value):
    try:
        with connect(host=Configs.host, database=Configs.database, user=Configs.user,
                     password=Configs.password, use_pure=True) as conn:
            cursor = conn.cursor()
            query = f'DELETE from {table} WHERE {where} = {where_value}'
            cursor.execute(query)
            conn.commit()

            return True
    except Error as e:
        print(f"Error: {e}")
    return False


def sql_execute(text: str):
    try:
        with connect(host=Configs.host, database=Configs.database, user=Configs.user,
                     password=Configs.password, use_pure=True) as conn:
            cursor = conn.cursor()
            query = str(text)
            cursor.execute(query)
            result = cursor.fetchall()
            conn.commit()
            return result
    except Error as e:
        print(f"Error: {e}")
        return False
