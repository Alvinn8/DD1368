import pandas as pd
import connect
from typing import List, Any, Tuple
from tabulate import tabulate
from colorama import Fore, Style

cur = connect.create_connection()

cur.execute("""
    PREPARE search_airport (text) AS
    SELECT name, iatacode, country FROM airport WHERE name ILIKE $1 OR iatacode ILIKE $1
    """
)

cur.execute("""
    PREPARE language_speakers (text) AS 
    SELECT
        country.name,
        ROUND(population * spoken.percentage / 100) AS numspeakers
    FROM spoken
    JOIN country
        ON spoken.country = country.code
    WHERE spoken.language = $1
    AND percentage IS NOT NULL
    """
)

cur.execute("""
    PREPARE country_code (text) AS
    SELECT
        name,
        code
    FROM country
    WHERE name = $1
    """
)

cur.execute("""
    PREPARE check_province (text) AS
    SELECT
        name,
        country
    FROM province
    WHERE name = $1
    AND country = $2
    """
)

class GeoCoord:
    def __init__(self, latitude : float, longitude : float):
        self.latitude = latitude
        self.longitude = longitude

def display_result(result, max_rows=10):
    # Convert result to DataFrame if it's not already
    df = pd.DataFrame(result)
    
    # Format numeric columns to avoid scientific notation and align properly
    df = df.map(lambda x: f"{x:,}" if isinstance(x, (int, float)) else str(x))

    # Determine if the DataFrame is too large
    total_rows = len(df)
    
    if total_rows > max_rows:
        # Calculate number of rows to show from head and tail
        head_rows = max_rows // 2
        tail_rows = max_rows - head_rows
        
        # Extract head and tail DataFrames
        head_df = df.head(head_rows)
        tail_df = df.tail(tail_rows)
        
        # Create a placeholder row
        placeholder = {col: "..." for col in df.columns}
        placeholder_df = pd.DataFrame([placeholder])
        
        # Combine head, placeholder, and tail
        display_df = pd.concat([head_df, placeholder_df, tail_df], ignore_index=True)
        row_split_message = f"... {total_rows - max_rows} rows hidden ..."
    else:
        display_df = df
        row_split_message = None

    # Convert DataFrame to a tabulated format
    table = tabulate(
        display_df,
        headers="keys",
        tablefmt="fancy_grid",
        showindex=False,
        stralign="left"  # Ensure all columns are left-aligned
    )
    
    # Add some color and emphasis
    print(f"{Fore.CYAN}{Style.BRIGHT}Result Summary:{Style.RESET_ALL}")
    print(table)
    
    # Display summary of hidden rows if applicable
    if row_split_message:
        print(f"{Fore.YELLOW}{row_split_message}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total Rows: {total_rows}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.GREEN}Displayed All Rows: {total_rows}{Style.RESET_ALL}\n")


def execute_statement(query : str, vars : List[Any]):
    cur.execute(query, vars)
    return cur.fetchall()

def search_airport(airport : str, max_rows=10) -> None:
    query_vars = ['%' + airport + '%']

    result = execute_statement(
        "EXECUTE search_airport (%s)", 
        query_vars
        )
    display_result(result, max_rows=max_rows)

def language_speakers(country_name : str, max_rows=10) -> None:
    query_vars = [country_name]

    result = execute_statement(
        "EXECUTE language_speakers (%s)", 
        query_vars
        )

    display_result(result, max_rows=max_rows)

def create_desert(
        name : str, 
        area : str, 
        province : str, 
        country : str,
        coordinates : GeoCoord,
        max_rows=10
        ) -> None:
    
    cur.execute(
        "EXECUTE country_code (%s)",
        [country]
    )

    country_codes = cur.fetchall()
    try:
        code = country_codes[0]["code"]
    except KeyError:
        print(f"Unkown country: {country}")
        return
    
    cur.execute(
        "EXECUTE check_province (%s, %s)",
        [province, code]
    )

    if len(cur.fetchall()) == 0:
        print(f"Unkown province {province}")
        return

    query_vars = [name, area, province, country, coordinates]

    result = execute_statement(
        "EXECUTE create_desert (%s)", 
        query_vars
        )

    display_result(result, max_rows=max_rows)

def parse_airport_args(inp_arr : List[str]):
    if len(inp_arr) == 2:
        search_airport(inp_arr[1])
        return
    elif len(inp_arr) == 3:
        search_airport(inp_arr[1], max_rows=int(inp_arr[2]))
        return

    print(f"Incorrect usage, expected 2 or 3 arguments got {len(inp_arr)}")

def parse_language_args(inp_arr : List[str]):
    if len(inp_arr) == 2:
        language_speakers(inp_arr[1])
        return
    elif len(inp_arr) == 3:
        language_speakers(inp_arr[1], max_rows=int(inp_arr[2]))
        return

    print(f"Incorrect usage, expected 2 or 3 arguments got {len(inp_arr)}")


def main():
    while True:
        inp = input("-> ").strip()
        inp_arr = inp.split()

        match inp_arr[0]:
            case "airport": parse_airport_args(inp_arr)
            case "language": parse_language_args(inp_arr)
            case _: print(f"Unkown command: {inp_arr[0]}")

if __name__ == "__main__":
    cur.execute("SELECT * FROM desert")
    display_result(cur.fetchall())

    # create_desert("test", "test", "Attikis", "Greece", GeoCoord(0, 0))

    main()