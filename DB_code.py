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
    pruefe_nach_schlagwort = execute_sql("SELECT kategorien.kategorienid FROM kategorien JOIN schlagwoerter ON kategorien.kategorienid = schlagwoerter.kategorienid WHERE schlagwoerter.wort = %s OR schlagwoerter.wort = %s",
                                         (Name_Empfaenger, Verwendungszweck), fetch=True)
    print(f"schlagwort{pruefe_nach_schlagwort}")
    if pruefe_nach_schlagwort:
        return execute_sql("INSERT INTO kontoeintrag (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email, kategorienid, kontoid) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email,pruefe_nach_schlagwort[0], kontoid,))
    else:
        return execute_sql(
            "INSERT INTO  kontoeintrag (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email, kategorienid, kontoid) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email, None, kontoid,))
def finde_kontoid_durch_namen(name, email):
    ergebnis = execute_sql("SELECT kontoid FROM konto_anlegen WHERE name = %s AND email = %s", (name, email), fetch=True)
    if ergebnis:
        kontoid = ergebnis[0][0]
        return kontoid
def letzten_kontoeintraege_zeigen(email, kontoid, anzahl_eintraege):
    if anzahl_eintraege == -1:  # Alle Einträge anzeigen
        eintrag = execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s ORDER BY zeitstempel", (email, kontoid), fetch=True)

    else:
        eintrag = execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s ORDER BY zeitstempel LIMIT %s", (email, kontoid, anzahl_eintraege), fetch=True)
    return eintrag
def finde_kontoid_name_email(email, name):
    kontid = execute_sql(" SELECT kontoid FROM konto_anlegen WHERE email=%s AND name =%s", (email, name), fetch=True)
    return kontid
def letzten_kontoeintraege_zeigen_5(email):
    eintrag =execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag  LEFT JOIN kategorien  ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s ORDER BY zeitstempel LIMIT 5", (email,), fetch=True)
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

#suchfunktion

def ergebnis_suchfunktion(email, kontoid, stichwort, startDate, endDate, betrag, empfaenger):
    # Grundlegende SQL-Abfrage
    sql_query = "SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s "
    sql_query_summe = "SELECT SUM(betrag) as Summe FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s "
    # Liste für die Parameter der Abfrage
    params = [email, kontoid]
    print(f"1{params}")
    # Bedingung für Verwendungszweck hinzufügen, falls vorhanden
    if stichwort:
        sql_query += "AND verwendungszweck = %s "
        sql_query_summe += "AND verwendungszweck = %s "
        params.append(f'{stichwort}')
        print(f"2{params}")

    # Datumsbereich zur Abfrage hinzufügen, wenn beide Daten vorhanden sind
    if startDate and endDate:
        sql_query += "AND zeitstempel BETWEEN %s AND %s "
        sql_query_summe += "AND zeitstempel BETWEEN %s AND %s "
        params.extend([startDate, endDate])
        print(f"3{params}")

    # Bedingung für betrag hinzufügen, wenn ein gültiger Wert angegeben ist
    if betrag not in [None, '', '0']:  # Angenommen, '0' ist ein ungültiger Wert für betrag
        sql_query += "AND betrag = %s "
        sql_query_summe += "AND betrag = %s "
        params.append(betrag)
        print(f"4{params}")

    # Bedingung für empfaenger hinzufügen
    if empfaenger:  # Nur hinzufügen, wenn empfaenger nicht leer ist
        sql_query += "AND Name_Empfaenger = %s "
        sql_query_summe += "AND Name_Empfaenger = %s "
        params.extend([f'{empfaenger}'])
        print(f"5{params}")

    # SQL-Abfrage ausführen
    erg_suchfunktion = execute_sql(sql_query, tuple(params), fetch=True)
    erg_summe = execute_sql(sql_query_summe, tuple(params), fetch=True)
    return erg_suchfunktion, erg_summe