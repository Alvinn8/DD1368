import psycopg2
from dotenv import load_dotenv
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


# Simple function to get all books with a specific genre.
def get_book_title_by_genre():
    genre = input("Please enter a genre: ")
    query = f"SELECT books.title FROM books LEFT JOIN genre ON books.bookid = genre.bookid WHERE genre.genre = '{genre}'"
    cur.execute(query)
    result = cur.fetchall()
    titles = [row[0] for row in result]

    print(titles)

if __name__ == "__main__":
    # Example:
    # Execute a query which returns all genres including the genre id.
    cur.execute("SELECT * from genre ")

    # Print the first row returned.
    print(cur.fetchone())
    
    # Print the next row returned.
    print(cur.fetchone())
    
    # Print all the remaining rows returned.
    print(cur.fetchall())
    
    # Close the connection to the database.
    conn.close()