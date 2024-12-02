from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
AUTH_CREDS = os.getenv('NEO4J_AUTH')
DB_HOST = os.getenv('NEO4J_URI_HOST')

URI = "neo4j://"+DB_HOST+":7687"
AUTH = (AUTH_CREDS.split("/")[0], AUTH_CREDS.split("/")[1])
driver = None
session = None

def open_db_connection():
    global driver, session
    driver = GraphDatabase.driver(URI, auth=AUTH)
    session = driver.session(database="neo4j")
    return session, driver

def close_db_connection():
    global driver, session
    if session is not None:
        session.close()
    if driver is not None:
        driver.close()
