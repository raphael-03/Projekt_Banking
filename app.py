from flask import Flask, render_template, request, redirect, url_for, session
import re
from DB_code import get_db_connection
app = Flask(__name__)
app.secret_key = 'AhmetundRaphael'

# Benutzerregistrierung und -anmeldung
@app.route('/', methods=['GET', 'POST'])
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

        error = None
        if len(passwort) < 8:
            error = 'Das Passwort muss mindestens 8 Zeichen lang sein.'
        elif not re.search("[A-Z]", passwort):
            error = 'Das Passwort muss mindestens einen Großbuchstaben enthalten.'
        elif not re.search("[a-z]", passwort):
            error = 'Das Passwort muss mindestens einen Kleinbuchstaben enthalten.'
        elif re.match("^[^A-Za-z0-9].*|.*[^A-Za-z0-9]$", passwort) or not re.search("[^A-Za-z0-9]", passwort):
            error = 'Das Passwort muss mindestens ein Sonderzeichen enthalten, das nicht am Anfang oder Ende steht.'
        elif passwort != passwort_repeat:
            error = 'Passwörter stimmen nicht überein.'

        # Fehlermeldung rendern
        if error:
            return render_template('registrierung.html', error=error, vorname=vorname, nachname=nachname,
                                   email=email, alter=alter, bankinstitut=bankinstitut, passwort=passwort,
                                   passwort_repeat=passwort_repeat)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM kunde WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return render_template('registrierung.html',error='Email existiert bereits',vorname=vorname, nachname=nachname
                                    ,email=email, alter=alter, bankinstitut=bankinstitut, password=passwort, passwort_repeat=passwort_repeat)
        # Füge in die Kunden Tabelle ein
        cur.execute("INSERT INTO kunde (vorname, nachname,email, alter, bankinstitut) VALUES (%s, %s, %s, %s, %s) RETURNING email",
                    (vorname, nachname, email, alter, bankinstitut))
        email = cur.fetchone()[0]
        print('test')
        # Füge kundenid und passwort in die Passwort Tabelle
        cur.execute("INSERT INTO passwort (email, passwort) VALUES (%s, %s)",
                    (email, passwort))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('startseite'))
    return render_template('registrierung.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT k.email FROM kunde k JOIN passwort p ON k.email = p.email WHERE k.email = %s AND p.passwort = %s",
                    (email, password))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            session['email'] = result[0]
            session['is_logged'] = True
            return redirect(url_for('startseite'))
        else:
            return render_template("login.html", error="Passwort ist falsch oder Kunde existiert nicht",email=email)
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    conn = get_db_connection()
    cur = conn.cursor()
    name_session = session.get("email")
    cur.execute("SELECT vorname FROM kunde k WHERE k.email= %s",(name_session,))
    name = cur.fetchone()[0]
    cur.close()
    conn.close()
    session.pop('email', None)
    return render_template('logout_page.html', name=name)

if __name__ == '__main__':
    app.run()
