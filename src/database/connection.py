from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import time

load_dotenv()

AUTH_CREDS = os.getenv('NEO4J_AUTH')
DB_HOST = os.getenv('NEO4J_URI_HOST')
DB_PORT = os.getenv('NEO4J_HOST_PORT')

URI = f"neo4j://{DB_HOST}:{DB_PORT}"
AUTH = tuple(AUTH_CREDS.split("/"))
driver = None
session = None
class DBConnection:
    def __init__(self):
        self.driver = None
        self.session = None

    def __enter__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.session = self.driver.session(database="neo4j")
        # Create constraints (if not already created)
        constraints = self.session.execute_read(lambda tx: tx.run("SHOW CONSTRAINTS YIELD name").values())
        existing_constraints = {row[0] for row in constraints}
        constraint_queries = {
            "gym_id": "CREATE CONSTRAINT gym_id FOR (n:Gym) REQUIRE n.id IS UNIQUE;",
            "user_id": "CREATE CONSTRAINT user_id FOR (n:User) REQUIRE n.id IS UNIQUE;",
            "post_id": "CREATE CONSTRAINT post_id FOR (n:Post) REQUIRE n.id IS UNIQUE;",
            "comment_id": "CREATE CONSTRAINT comment_id FOR (n:Comment) REQUIRE n.id IS UNIQUE;",
            "reaction_id": "CREATE CONSTRAINT reaction_id FOR (n:Reaction) REQUIRE n.id IS UNIQUE;"
        }
        for name, query in constraint_queries.items():
            if name not in existing_constraints:
                self.session.execute_write(lambda tx: tx.run(query))
        # Return the driver so that functions can use driver.execute_query
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session:
            self.session.close()
        if self.driver:
            self.driver.close()
