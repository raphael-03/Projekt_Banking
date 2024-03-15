import psycopg2
import os


def get_db_connection():
    host = "localhost"
    database = "postgres"
    user = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    return conn


def execute_sql(sql, values=None, fetch=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, values)
        if fetch:
            return cur.fetchall()
        conn.commit()
    except psycopg2.DatabaseError as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def register_user(vorname, nachname, email, alter, bankinstitut, password):
    user_exists = execute_sql("SELECT * FROM kunde WHERE email = %s", (email,), fetch=True)
    if user_exists:
        return 'Email existiert bereits'

    execute_sql(
        "INSERT INTO kunde (vorname, nachname, email, alter, bankinstitut) VALUES (%s, %s, %s, %s, %s)",
        (vorname, nachname, email, alter, bankinstitut)
    )

    user_email = execute_sql("SELECT email FROM kunde WHERE email = %s", (email,), fetch=True)
    if user_email:
        print(user_email[0][0])
        execute_sql(
            "INSERT INTO password (email, password) VALUES (%s, %s)",
            (user_email[0][0], password)
        )


def login_user(email, password):
    return execute_sql(
        "SELECT k.email FROM kunde k JOIN password p ON k.email = p.email WHERE k.email = %s AND p.password = %s",
        (email, password),
        fetch=True
    )


def logout_user(email):
    return execute_sql(
        "SELECT vorname FROM kunde WHERE email = %s",
        (email,),
        fetch=True
    )


def konto_anlegen(name, email):
    return execute_sql(
        "INSERT INTO konto_anlegen (name, email) VALUES (%s,%s)",
        (name, email,))

def konto_anzeigen(email):
    return execute_sql("SELECT name FROM konto_anlegen WHERE email = %s", (email,), fetch=True)

def pruefe_konto(email):
    konto_existiert = execute_sql("SELECT * FROM konto_anlegen WHERE email =%s", (email,), fetch=True)
    if konto_existiert:
        return True
    return False

def create_kontoauszug_anlegen(Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email, kontoid):
    return execute_sql("INSERT INTO Kontoeintrag (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck,email,  kontoid) VALUES (%s, %s, %s, %s, %s, %s)", (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck,email, kontoid))

def finde_kontoid_durch_namen(name, email):
    ergebnis = execute_sql("SELECT kontoid FROM konto_anlegen WHERE name = %s AND email = %s", (name, email), fetch=True)
    if ergebnis:
        kontoid = ergebnis[0][0]
        return kontoid
def letzten_kontoeintraege_zeigen(email):
    eintrag =execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, name  FROM kontoeintrag  LEFT JOIN kategorien  ON kontoeintrag.kontoeintragid = kategorien.kategorienid WHERE kontoeintrag.email = %s ORDER BY zeitstempel LIMIT 15", (email,), fetch=True)
    return eintrag

def letzten_kontoeintraege_zeigen_5(email):
    eintrag =execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, name FROM kontoeintrag  LEFT JOIN kategorien  ON kontoeintrag.kontoeintragid = kategorien.kategorienid WHERE kontoeintrag.email = %s ORDER BY zeitstempel LIMIT 5", (email,), fetch=True)
    return eintrag

def letzten_kontoeintraege_zeigen30(email):
    eintrag =execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, name  FROM kontoeintrag  LEFT JOIN kategorien  ON kontoeintrag.kontoeintragid = kategorien.kategorienid WHERE kontoeintrag.email = %s ORDER BY zeitstempel LIMIT 30", (email,), fetch=True)
    return eintrag

def kategorien_erstellen(email, name):
    pruefe = execute_sql("SELECT name FROM kategorien WHERE name=%s", (name,), fetch=True)
    if pruefe:
        return 'Kategorie existiert bereits'
    else:
        kategorien = execute_sql("INSERT INTO kategorien(email, name) VALUES (%s, %s)", (email, name,))
        return kategorien

def kategorien_waehlen(email):
    return execute_sql("SELECT name,kategorienid FROM kategorien WHERE email=%s", (email,), fetch=True)

def schlagwort_einfuegen(kategorienid, wort):
    return execute_sql("INSERT INTO schlagwoerter(kategorienid, wort) VALUES (%s, %s)", (kategorienid, wort))

def kategorien_erstellen_2(email, name, schlagwoerter):
    execute_sql("INSERT INTO kategorien(email, name) VALUES (%s, %s);", (email, name))
    ergebnis = execute_sql("SELECT * FROM kategorien WHERE email=%s AND name=%s", (email, name), fetch=True)
    print(f"Ergebnis{ergebnis}")
    if ergebnis:
        kategorienid = ergebnis[0][0]
        print(kategorienid)
        print(f"1{schlagwoerter}")
        if isinstance(schlagwoerter, str):
            schlagwoerter = [wort.strip() for wort in schlagwoerter.split(',')]
        for wort in schlagwoerter:
            print(f"2{wort}")
            execute_sql("INSERT INTO schlagwoerter(kategorienid, wort) VALUES (%s, %s)", (kategorienid, wort))
        return email, print("fertig")
    else:
        print("Fehler")

    return email