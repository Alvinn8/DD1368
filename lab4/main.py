import pandas as pd
import connect
from typing import List, Any, Set, Tuple
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

cur.execute("""
    PREPARE get_province (text) AS
    SELECT
        province
    FROM geo_desert
    WHERE desert = $1
    """
)

cur.execute("""
    PREPARE get_deserts (text) AS
    SELECT
        desert
    FROM geo_desert
    WHERE country = $1
    """
)

cur.execute("""
    PREPARE get_desert_area (text) AS
    SELECT
        area
    FROM desert
    WHERE name = $1
    """
)

cur.execute("""
    PREPARE get_province_area (text) AS
    SELECT
        area
    FROM province
    WHERE name = $1
    """
)

cur.execute("""
    PREPARE insert_desert (text) AS
    INSERT INTO desert (name, area, coordinates) 
    VALUES (
        $1, $2, $3
    )
    ON CONFLICT DO NOTHING
    """
)

cur.execute("""
    PREPARE insert_geo_desert (text) AS
    INSERT INTO geo_desert (desert, country, province) 
    VALUES (
        $1, $2, $3
    )
    """
)

cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
""")

TABLES = [t["table_name"] for t in cur.fetchall()]

class GeoCoord:
    def __init__(self, latitude : float, longitude : float):
        self.latitude = latitude
        self.longitude = longitude

    @property
    def as_tuple(self) -> Tuple[float]:
        return (self.latitude, self.longitude)
    
    @classmethod
    def from_string(cls, coord_string: str):
        # Remove parentheses and split the string by the comma
        try:
            stripped = coord_string.strip("()")
            lat_str, lon_str = stripped.split(",")
            latitude = float(lat_str)
            longitude = float(lon_str)
            return cls(latitude, longitude)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid coordinate string: {coord_string}")


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

def display_table(table : str, max_rows=10):
    # check that the table exists, avoids SQL-injection
    if table in TABLES:
        cur.execute(f"SELECT * FROM {table}")
        res = cur.fetchall()
        display_result(res, max_rows=max_rows)
    else:
        print(f"Unkown table {table}")

def fetch_query(query : str, vars : List[Any]):
    cur.execute(query, vars)
    return cur.fetchall()

def query(query : str, vars : List[Any]):
    cur.execute(query, vars)

def search_airport(airport : str, max_rows=10) -> None:
    query_vars = ['%' + airport + '%']

    result = fetch_query(
        "EXECUTE search_airport (%s)", 
        query_vars
        )
    display_result(result, max_rows=max_rows)

def language_speakers(country_name : str, max_rows=10) -> None:
    query_vars = [country_name]

    result = fetch_query(
        "EXECUTE language_speakers (%s)", 
        query_vars
        )

    display_result(result, max_rows=max_rows)

def get_country_code(country : str) -> str:
    # Fetch the country code
    cur.execute(
        "EXECUTE country_code (%s)",
        [country]
    )

    country_codes = cur.fetchall()

    # Check that the country exists, and get the country code
    try:
        code = country_codes[0]["code"]
        return code
    except KeyError:
        return None

def get_provinces(desert : str) -> Set[str]:
    cur.execute(
        "EXECUTE get_province (%s)",
        [desert]
    )

    provinces = cur.fetchall()

    return set([p["province"] for p in provinces])

def get_deserts(country_code : str) -> Set[str]:
    cur.execute(
        "EXECUTE get_deserts (%s)",
        [country_code]
    )

    deserts = cur.fetchall()

    return set([d["desert"] for d in deserts])

def get_desert_area(desert : str) -> int:
    cur.execute(
        "EXECUTE get_desert_area (%s)",
        [desert]
    )

    area = cur.fetchall()

    if len(area) != 0:
        return area[0]["area"]
    return None

def get_province_area(province : str) -> int:
    cur.execute(
        "EXECUTE get_province_area (%s)",
        [province]
    )

    area = cur.fetchall()

    if len(area) != 0:
        return area[0]["area"]
    return None

def province_exists(province : str, country_code : str) -> bool:
    cur.execute(
        "EXECUTE check_province (%s, %s)",
        [province, country_code]
    )

    return not len(cur.fetchall()) == 0

def desert_exists(desert : str) -> bool:
    get_desert_area(desert) is not None

def create_desert(
        name : str, 
        area : int,
        province : str, 
        country : str,
        coordinates : GeoCoord
        ) -> None:
    
    code = get_country_code(country)

    if code is None:
        print(f"Unkown country: {country}.")
        return
    
    if not province_exists(province, code):
        print(f"Unkown province: {province}. Could not find {province} in {country}.")
        return
    
    if len(d := get_deserts(code)) >= 20:
        print(f"Countries cannot have more than 20 deserts. Current deserts {d}")
        return

    # If the desert is already in the database, use the existing value instead of input value
    desert_area = get_desert_area(name)
    area = desert_area if desert_area is not None else area

    # Make sure to include the province provided by the user
    provinces = get_provinces(name).union(set([province]))

    if len(provinces) >= 9:
        print(f"Desert cannot span more than 9 provinces. Currently spans {provinces}")
        return

    for prov in provinces:
        prov_area = get_province_area(prov)
        if prov_area is not None and area > 30 * prov_area:
            print(f"A desert can be at most 30 times larger than any province it resides in. Area {area} too large for {province}, which has an area of {prov_area}!")

    geo_vars = [name, code, province]
    desert_vars = [name, area, coordinates.as_tuple]

    if not desert_exists(name):
        query(
        "EXECUTE insert_desert (%s, %s, %s)", 
        desert_vars
        )

    query(
        "EXECUTE insert_geo_desert (%s, %s, %s)", 
        geo_vars
        )
    cur.connection.commit()

def parse_airport_args(inp_arr : List[str]):
    try:
        if len(inp_arr) == 2:
            search_airport(inp_arr[1])
            return
        elif len(inp_arr) == 3:
            search_airport(inp_arr[1], max_rows=int(inp_arr[2]))
            return
    except Exception as e:
        print(e)
        return

    print(f"Incorrect usage, expected 2 or 3 arguments got {len(inp_arr) - 1}")

def parse_language_args(inp_arr : List[str]):
    try: 
        if len(inp_arr) == 2:
            language_speakers(inp_arr[1])
            return
        elif len(inp_arr) == 3:
            language_speakers(inp_arr[1], max_rows=int(inp_arr[2]))
            return
    except Exception as e:
        print(e)
        return

    print(f"Incorrect usage, expected 2 or 3 arguments got {len(inp_arr) - 1}")

def parse_desert_args(inp_arr : List[str]):
    if len(inp_arr) != 6:
        print(f"Incorrect usage, expected 5 arguments got {len(inp_arr) - 1}")
        return

    try: 
        create_desert(inp_arr[1], int(inp_arr[2]), inp_arr[3], inp_arr[4], GeoCoord(inp_arr[5]))
    except Exception as e:
        print(e)

def parse_display_args(inp_arr : List[str]):
    try: 
        if len(inp_arr) == 2:
            display_table(inp_arr[1])
            return
        elif len(inp_arr) == 3:
            display_table(inp_arr[1], max_rows=int(inp_arr[2]))
            return
    except Exception as e:
        print(e)
        return

    print(f"Incorrect usage, expected 2 or 3 arguments got {len(inp_arr) - 1}")

def print_help_page():
    """
    Prints a formatted help page for the available commands.
    """
    print("\n" + "=" * 107)
    print("            HELP PAGE")
    print("=" * 107)
    print("Available Commands:")
    print()
    print("  airport [name] [rows (optional)]                         - Search airports by name or IATA code")
    print("  language [language] [rows (optional)]                    - Search countries that speak the given language")
    print("  cdesert [name] [area] [province] [country] [coordinates] - Create desert")
    print("  display [table name] [rows (optional)]                   - Display table")
    print("  exit                                                     - Exit the program")

    print("=" * 107 + "\n")

def main():
    while True:
        inp = input("-> ").strip()
        inp_arr = inp.split()

        match inp_arr[0]:
            case "airport": parse_airport_args(inp_arr)
            case "language": parse_language_args(inp_arr)
            case "cdesert": parse_desert_args(inp_arr)
            case "display": parse_display_args(inp_arr)
            case "help": print_help_page()
            case "exit": break
            case _: print(f"Unkown command: {inp_arr[0]}")

if __name__ == "__main__":
    # create_desert("test", 100, "Attikis", "Greece", GeoCoord(0, 0))

    main()