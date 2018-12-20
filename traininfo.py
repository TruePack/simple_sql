from jinja2 import Environment, FileSystemLoader
import psycopg2
import requests
import traceback
import os

# open connect to postgres with context manager
with psycopg2.connect(
    # options for connection
    host="localhost",
    database="user",
    user="user",
    password="user123",
) as conn:
    with conn.cursor() as cur:
        try:
            # try create table with some fields
            cur.execute("""
                CREATE TABLE
                    ALFACON (
                        EMPFIO VARCHAR,
                        NUMBER INT,
                        INSPOINTNAME VARCHAR,
                        TRAINNAME VARCHAR,
                        REPTYPENAME VARCHAR,
                        DEFECTIONDATETIME REAL,
                        WAGONNUMBER VARCHAR,
                        DEFECTNAME VARCHAR,
                        CNTFOUND INT,
                        CNTFIXED INT,
                        DESCRIPTION VARCHAR
                    );
            """)
            # take massive of data from site
            req = requests.get("http://api.techgroup.su/actsListPub")
            # convert massive to list of dicts
            data = req.json()
            # create list of fields for insert data in them (for columns name)
            fields = [
                "EMPFIO",
                "NUMBER",
                "INSPOINTNAME",
                "TRAINNAME",
                "REPTYPENAME",
                "DEFECTIONDATETIME",
                "WAGONNUMBER",
                "DEFECTNAME",
                "CNTFOUND",
                "CNTFIXED",
                "DESCRIPTION",
            ]
            for item in data:
                # list comprehensions for every value in data and take it for fields
                my_data = [item[field] for field in fields]
                # insert values in table
                cur.execute(
                    "INSERT INTO ALFACON VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    tuple(my_data),
                )
        except Exception:
            # if while transaction have some error then print this error and cancel transaction
            traceback.print_exc()
            cur.execute("ROLLBACK")
        # select values from columns with trainname == 'ЭР2Р-7022'
        cur.execute(
            """
                SELECT WAGONNUMBER, DEFECTNAME, CNTFOUND, CNTFIXED
                FROM ALFACON
                WHERE TRAINNAME = 'ЭР2Р-7022';
                """
        )
        # for save selected values
        selected_table = cur.fetchall()
# to create table with result of select
# open file (or create then open if not exist) for write result with context manager
with open("final_template.html", "w") as html:
    # jinja`s environment == 'pwd'
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
    )
    # jinja`s template is template.html
    template = env.get_template("template.html")
    # pass result of select to template
    output_from_parsed_template = template.render(selected_table=selected_table)
    # then write it
    html.write(output_from_parsed_template)
