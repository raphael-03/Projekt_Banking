import os
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"]
)

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS kunde, passwort")

cur.execute("""
CREATE TABLE kunde (
    kundenid serial PRIMARY KEY,
    email varchar(100),
    vorname varchar(50),
    nachname varchar(100),
    alter integer,
    bankinstitut varchar(100)
);
""")

cur.execute("""
CREATE TABLE passwort (
    kundenid serial PRIMARY KEY,
    passwort text);
""")


conn.commit()

cur.close()
conn.close()