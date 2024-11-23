from database.connection import open_db_connection, close_db_connection

def use_db_connection(func):
    def wrapper(*args, **kwargs):
        _, driver = open_db_connection()
        result = func(driver=driver,*args, **kwargs)
        close_db_connection()
        return result
    return wrapper
