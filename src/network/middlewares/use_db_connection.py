from database.connection import DBConnection

def use_db_connection(func):
    def wrapper(*args, **kwargs):
        with DBConnection() as driver:
            return func(driver=driver, *args, **kwargs)
    return wrapper