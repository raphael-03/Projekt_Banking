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
    Zeitstempel date,
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


cur.execute("""
INSERT INTO kunde(email, vorname, nachname, alter,bankinstitut ) VALUES(
        'raphi23@mail.de', 'Raphael', 'Schmidt', 22, 'Sparkasse')""")

cur.execute("""
INSERT INTO password(email, password) VALUES(
        'raphi23@mail.de', 'Raph#ael23'
)""")

cur.execute("""
INSERT INTO konto_anlegen(kontoid,name, email) VALUES(
        1234,'test1', 'raphi23@mail.de'
)""")
cur.execute("""
INSERT INTO konto_anlegen(kontoid,name, email) VALUES(
        1200,'Konto2', 'raphi23@mail.de'
)""")

cur.execute("""
INSERT INTO kategorien (kategorienid,email, name) VALUES (1001,'raphi23@mail.de', 'Essen')
""")
cur.execute("""
INSERT INTO kategorien (kategorienid,email, name) VALUES (1002,'raphi23@mail.de', 'auto')
""")
cur.execute("""INSERT INTO schlagwoerter (schlagwoerterid, kategorienid, wort) VALUES (2001, 1001, 'Edeka')""")
cur.execute("""INSERT INTO schlagwoerter (schlagwoerterid, kategorienid, wort) VALUES (2002, 1001, 'Rewe')""")
cur.execute("""INSERT INTO schlagwoerter (schlagwoerterid, kategorienid, wort) VALUES (2003, 1001, 'lidl')""")
cur.execute("""INSERT INTO schlagwoerter (schlagwoerterid, kategorienid, wort) VALUES (2004, 1002, 'auto')""")

sql_eintraege="""INSERT INTO Kontoeintrag(Zeitstempel,Betrag, Name_Empfaenger, Verwendungszweck,kategorienid ,email, kontoid )
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
benutzer_eintraege= [
    ('2024-03-06', 100, 'Tim', 'Edeka',1001,'raphi23@mail.de', 1234),
    ('2024-03-07', 100, 'Tim', 'Rewe',1001,'raphi23@mail.de', 1200),
    ('2024-03-08', 100, 'Edeka','auto',1002,'raphi23@mail.de', 1234)
]
cur.executemany(sql_eintraege, benutzer_eintraege)

conn.commit()

cur.close()
conn.close()