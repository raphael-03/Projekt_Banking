from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
app = Flask(__name__)

#Datenbank verbindung
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"])
    return conn

# Benutzerregistrierung und -anmeldung
@app.route('/')
def startseite():
    return render_template("startseite.html")

@app.route('/registrierung',methods=['GET', 'POST'])
def registrierung():
    if request.method == 'POST':
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        email = request.form.get('email')
        alter = request.form.get('alter')
        bankinstitut = request.form.get('bankinstitut')
        passwort = request.form['passwort']
        passwort_repeat = request.form['passwort_repeat']

        if passwort != passwort_repeat:
            return render_template('registrierung.html', error='Passwörter stimmen nicht überein', vorname=vorname, nachname=nachname
                                    ,email=email, alter=alter, bankinstitut=bankinstitut, password=passwort, passwort_repeat=passwort_repeat)
    return render_template('registrierung.html')

if __name__ == '__main__':
    app.run()
