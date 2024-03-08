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
        execute_sql(
            "INSERT INTO passwort (email, password) VALUES (%s, %s)",
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
        (email[0]),
        fetch=True
    )


def konto_anlegen(name, email):
    print("Konto anlegen")
    return execute_sql(
        "INSERT INTO konto_anlegen (name, email) VALUES (%s,%s)",
        (name, email,),
        fetch=True)


def create_kontoauszug_anlegen(zeitstempel, betrag, empfaenger, verwendungszweck):
    return execute_sql(

    )
