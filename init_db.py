import os
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"]
)

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS kunde, password,Konto_anlegen,Kontoeintrag, kategorien, schlagwoerter")

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
CREATE TABLE password (
    email varchar(100) references kunde(email),
    password text);
""")

cur.execute("""
CREATE TABLE konto_anlegen (
    kontoid SERIAL PRIMARY KEY,
    name varchar(100),
    email varchar(100) references kunde(email) 
);
""")
cur.execute("""
CREATE TABLE kategorien(
    kategorienid SERIAL PRIMARY KEY,
    email varchar(100) references kunde(email),
    name varchar(255) NOT NUll);

""")

cur.execute("""
CREATE TABLE Kontoeintrag (
    kontoeintragid SERIAL PRIMARY KEY,
    Zeitstempel TIMESTAMP,
    Betrag decimal,
    Name_Empfaenger varchar(100),
    Verwendungszweck varchar(100),
    kategorienid integer references kategorien(kategorienid),
    email varchar(100) references kunde(email),
    kontoid integer references konto_anlegen(kontoid)
)
""")

cur.execute("""
CREATE TABLE schlagwoerter(
    schlagwoerterid SERIAL PRIMARY KEY,
    kategorienid integer references kategorien(kategorienid),
    wort VARCHAR(255) NOT NULL);
""")
conn.commit()

cur.close()
conn.close()