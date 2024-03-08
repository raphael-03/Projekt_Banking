import psycopg2, os

#Datenbank verbindung
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"])
    return conn