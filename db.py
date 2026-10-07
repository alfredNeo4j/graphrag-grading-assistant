"""Shared Neo4j connection helper. Reads credentials from .env."""
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def get_driver():
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
    )
    driver.verify_connectivity()
    return driver


def run(driver, query, **params):
    """Run a parameterised query and return a list of dict rows."""
    records, _, _ = driver.execute_query(query, params, database_=DATABASE)
    return [r.data() for r in records]
