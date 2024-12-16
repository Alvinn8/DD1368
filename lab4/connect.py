import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

import psycopg2._psycopg
load_dotenv()

"""
Note: It's essential never to include database credentials in code pushed to GitHub. 
Instead, sensitive information should be stored securely and accessed through environment variables or similar. 
However, in this particular exercise, we are allowing it for simplicity, as the focus is on a different aspect.
Remember to follow best practices for secure coding in production environments.
"""


def create_connection() -> psycopg2._psycopg.cursor:
    # Acquire a connection to the database by specifying the credentials.
    conn = psycopg2.connect(
        host=os.getenv("HOST"), 
        database=os.getenv("DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
        )

    # Create a cursor. The cursor allows you to execute database queries.
    cur = conn.cursor(cursor_factory=RealDictCursor)

    return cur