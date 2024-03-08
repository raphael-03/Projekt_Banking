import os
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"]
)

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS kunde, password,Konto_anlegen,Kontoeintrag")

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
    email varchar(100) PRIMARY KEY,
    password text);
""")

cur.execute("""
CREATE TABLE Konto_anlegen (
    kontoid integer PRIMARY KEY,
    name varchar(100) NOT NULL,
    email varchar(100) NOT NULL,
    FOREIGN KEY (email) REFERENCES kunde(email)
);
""")

cur.execute("""
CREATE TABLE Kontoeintrag (
    kontoeintragid integer PRIMARY KEY,
    Zeitstempel date,
    Betrag decimal,
    Name_Empfaenger varchar(100),
    Verwendungszweck varchar(100),
    kontoid integer not null ,
    FOREIGN KEY (kontoid) REFERENCES konto_anlegen(kontoid)
)
""")
cur.execute("""
INSERT INTO kunde(email, vorname, nachname, alter,bankinstitut ) VALUES(
        'raphi23@mail.de', 'Raphael', 'Schmidt', 22, 'Sparkasse')""")

cur.execute("""
INSERT INTO password(email, password) VALUES(
        'raphi23@mail.de', 'Raph#ael23'
)""")

conn.commit()

cur.close()
conn.close()