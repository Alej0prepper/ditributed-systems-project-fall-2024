from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
PASS = os.getenv('PASS')

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", PASS)
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
