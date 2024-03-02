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
    email varchar(100) PRIMARY KEY,
    vorname varchar(50),
    nachname varchar(100),
    alter integer,
    bankinstitut varchar(100)
);
""")

cur.execute("""
CREATE TABLE passwort (
    email varchar(100) PRIMARY KEY,
    passwort text);
""")

cur.execute("""
CREATE TABLE Konto_anlegen (
    kontoid integer PRIMARY KEY,
    name varchar(100) NOT NULL,
    FOREIGN KEY (email) REFERENCES kunde(email);
)
""")

cur.execute("""
CREATE TABLE Kontoeintrag (
    kontoeintragid integer PRIMARY KEY,
    Zeitstempel date,
    Betrag integer decimal,
    Name_Empfaenger varchar(100),
    Verwendungszweck varchar(100),
    FOREIGN KEY (Konto_anlegen) REFERENCES konto_anlegen(kontoid)
)
""")


conn.commit()

cur.close()
conn.close()