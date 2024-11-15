from src.database.connection import open_db_connection, close_db_connection

session, driver = open_db_connection()
driver.execute_query("match (n:User) -[r:Posts]-> (n1:Post) delete r")
driver.execute_query("match (n:User) -[r:Reposts]-> (n1:Post) delete r")
driver.execute_query("match (n:User) -[r:Follows]-> (n1:User) delete r")
driver.execute_query("match (c:Comment) -[r:Has]-> (c1:Comment) delete r")
driver.execute_query("match (p:Post) -[r:Has]-> (c1:Comment) delete r")
driver.execute_query("match (u:User) -[r:Comments]-> (c1:Comment) delete r")

driver.execute_query("match (n) delete n")

close_db_connection()

