import psycopg2
import os
import pandas as pd
import io

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

def login_user(email):
    return execute_sql(
        "SELECT email, password FROM password WHERE email = %s;",(email,),fetch=True)
def logout_user(email):
    return execute_sql(
        "SELECT vorname FROM kunde WHERE email = %s",(email,),fetch=True)
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
    eintrag =execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag  LEFT JOIN kategorien  ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s ORDER BY zeitstempel DESC LIMIT 5", (email,), fetch=True)
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
            kategorie_zu_kontoeintraegen_zuordnen(kategorienid, schlagwoerter)
        return email, print("fertig")
    else:
        print("Fehler")

    return email

# Wenn eine neue Kategorie erstellt wird, werden die Kontoeinträge überprüft, ob sie der neuen Kategorie zugeordnet werden können
def kategorie_zu_kontoeintraegen_zuordnen(kategorienid, schlagwoerter):
    for wort in schlagwoerter:
        # Wir suchen nach Kontoeinträgen, deren Verwendungszweck eines der Schlagwörter enthält
        eintraege = execute_sql("SELECT kontoeintragid FROM Kontoeintrag WHERE Verwendungszweck LIKE %s", ('%' + wort + '%',), fetch=True)
        for eintrag in eintraege:
            # Aktualisieren den Kontoeintrag mit der kategorienid
            execute_sql("UPDATE Kontoeintrag SET kategorienid=%s WHERE kontoeintragid=%s", (kategorienid, eintrag[0]))
#suchfunktion

def ergebnis_suchfunktion(email, kontoid, stichwort, startDate, endDate, betrag, empfaenger):
    sql_query = "SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s "
    sql_query_summe = "SELECT SUM(betrag) as Summe FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s "

    params = [email, kontoid]
    # Bedingung für Verwendungszweck hinzufügen, falls vorhanden
    if stichwort:
        sql_query += "AND verwendungszweck = %s "
        sql_query_summe += "AND verwendungszweck = %s "
        params.append(f'{stichwort}')

    # Datumsbereich zur Abfrage hinzufügen, wenn beide Daten vorhanden sind
    if startDate and endDate:
        sql_query += "AND zeitstempel BETWEEN %s AND %s "
        sql_query_summe += "AND zeitstempel BETWEEN %s AND %s "
        params.extend([startDate, endDate])

    # Bedingung für betrag hinzufügen, wenn ein gültiger Wert angegeben ist
    if betrag not in [None, '', '0']:
        sql_query += "AND betrag = %s "
        sql_query_summe += "AND betrag = %s "
        params.append(betrag)


    # Bedingung für empfaenger hinzufügen
    if empfaenger:
        sql_query += "AND Name_Empfaenger = %s "
        sql_query_summe += "AND Name_Empfaenger = %s "
        params.extend([f'{empfaenger}'])

    erg_suchfunktion = execute_sql(sql_query, tuple(params), fetch=True)
    erg_summe = execute_sql(sql_query_summe, tuple(params), fetch=True)
    return erg_suchfunktion, erg_summe

# Excel export
def excel_export(email,kontoid):
    sql_excel =execute_sql("SELECT Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, kategorien.name FROM kontoeintrag LEFT JOIN kategorien ON kontoeintrag.kategorienid = kategorien.kategorienid WHERE kontoeintrag.email = %s AND kontoeintrag.kontoid = %s ORDER BY zeitstempel", (email, kontoid),fetch=True)
    df = pd.DataFrame(sql_excel)
    output = io.BytesIO()
    # Erstellen der Excel-Datei im Speicher
    with pd.ExcelWriter(output, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name='Sheet1')
    output.seek(0)
    return output

# excel import SQL input
def insert_into_database(df, email, kontoid):
    ergebnisse = []  # Zum Speichern der Ergebnisse oder Erfolgs-/Fehlermeldungen
    for index, row in df.iterrows():
        pruefe_nach_schlagwort = execute_sql(
            "SELECT kategorien.kategorienid FROM kategorien JOIN schlagwoerter ON kategorien.kategorienid = schlagwoerter.kategorienid WHERE schlagwoerter.wort = %s OR schlagwoerter.wort = %s",
            (row['Empfaenger'], row['Verwendungszweck']), fetch=True)

        if pruefe_nach_schlagwort:
            kategorienid = pruefe_nach_schlagwort[0][
                0]  # Annahme, dass pruefe_nach_schlagwort eine Liste von Tupeln ist
            ergebnis = execute_sql(
                "INSERT INTO kontoeintrag (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email, kategorienid, kontoid) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (row['Zeitstempel'], row['Betrag'], row['Empfaenger'], row['Verwendungszweck'], email, kategorienid,
                 kontoid,))
        else:
            ergebnis = execute_sql(
                "INSERT INTO kontoeintrag (Zeitstempel, Betrag, Name_Empfaenger, Verwendungszweck, email, kategorienid, kontoid) VALUES (%s, %s, %s, %s, %s, NULL, %s)",
                (row['Zeitstempel'], row['Betrag'], row['Empfaenger'], row['Verwendungszweck'], email, kontoid,))

        ergebnisse.append(ergebnis)
    return ergebnisse

#visualiserung der EInträge

def sortieren_nach_kategorien(email, kontoid, jahr=None, monat=None, start_datum=None, ende_datum=None):
    base_query = "SELECT COALESCE(k.name, 'Keine Kategorie') AS Kategorie, ke.Zeitstempel, ke.Betrag, ke.Name_Empfaenger, ke.Verwendungszweck FROM Kontoeintrag ke LEFT JOIN kategorien k ON ke.kategorienid = k.kategorienid WHERE ke.email = %s AND ke.kontoid = %s"
    params = [email, kontoid]

    if jahr and monat:
        base_query += " AND EXTRACT(YEAR FROM ke.Zeitstempel) = %s AND EXTRACT(MONTH FROM ke.Zeitstempel) = %s"
        params.extend([jahr, monat])
    elif monat:
        base_query += " AND EXTRACT(MONTH FROM ke.Zeitstempel) = %s"
        params.append(monat)
    elif jahr:
        base_query += " AND EXTRACT(YEAR FROM ke.Zeitstempel) = %s"
        params.append(jahr)
    elif start_datum and ende_datum:
        base_query += "AND zeitstempel BETWEEN %s AND %s "
        params.extend([start_datum, ende_datum])

    base_query += " ORDER BY Kategorie, ke.Zeitstempel"
    eintraege = execute_sql(base_query, tuple(params), fetch=True)
    return eintraege


def get_kategorie_summen(email, kontoid, jahr=None, monat=None, start_datum=None, ende_datum=None):
    base_query = "SELECT COALESCE(k.name, 'Keine Kategorie') AS Kategorie, SUM(ke.Betrag) AS Gesamtsumme FROM Kontoeintrag ke LEFT JOIN kategorien k ON ke.kategorienid = k.kategorienid WHERE ke.email = %s AND ke.kontoid = %s"
    params = [email, kontoid]

    if jahr and monat:
        base_query += " AND EXTRACT(YEAR FROM ke.Zeitstempel) = %s AND EXTRACT(MONTH FROM ke.Zeitstempel) = %s"
        params.extend([jahr, monat])
    elif monat:
        base_query += " AND EXTRACT(MONTH FROM ke.Zeitstempel) = %s"
        params.append(monat)
    elif jahr:
        base_query += " AND EXTRACT(YEAR FROM ke.Zeitstempel) = %s"
        params.append(jahr)

    elif start_datum and ende_datum:
        base_query += "AND zeitstempel BETWEEN %s AND %s "
        params.extend([start_datum, ende_datum])

    base_query += " GROUP BY Kategorie ORDER BY Gesamtsumme DESC"
    kategorie_summe = execute_sql(base_query, tuple(params), fetch=True)
    return kategorie_summe

def finde_konto_name(email, kontoid):
    konto_name = execute_sql("SELECT name FROM konto_anlegen WHERE email = %s AND kontoid = %s", (email,kontoid,), fetch=True)
    return konto_name[0][0]