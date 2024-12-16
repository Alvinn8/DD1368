import psycopg2
from dotenv import load_dotenv
import pandas as pd
import os

"""
Note: It's essential never to include database credentials in code pushed to GitHub. 
Instead, sensitive information should be stored securely and accessed through environment variables or similar. 
However, in this particular exercise, we are allowing it for simplicity, as the focus is on a different aspect.
Remember to follow best practices for secure coding in production environments.
"""

load_dotenv()

# Acquire a connection to the database by specifying the credentials.
conn = psycopg2.connect(
    host=os.getenv("HOST"), 
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD")
    )
print(conn)

# Create a cursor. The cursor allows you to execute database queries.
cur = conn.cursor()

def to_dict(column_names, values):
    return {k : v for (k, v) in zip(column_names, values)}

def display_result(columns, result):
    rows = [[x[i] for x in result] for i in range(len(columns))]
    d = to_dict(columns, rows)
    df = pd.DataFrame.from_dict(d)
    print(df)

def search_airport(airport_name : str) -> None:
    columns = ["name", "iatacode", "country"]

    query = f"SELECT {','.join(columns)} FROM airport WHERE name ILIKE '%%{airport_name}%%'"
    cur.execute(query)
    result = cur.fetchall()

    display_result(columns, result)


if __name__ == "__main__":

    search_airport(input("Search airport: "))
    conn.close()