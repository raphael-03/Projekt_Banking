from flask import Flask, render_template, request, redirect, url_for, session
import re
from DB_code import get_db_connection, execute_sql, register_user, login_user, logout_user, konto_anlegen
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
        password = request.form['password']
        password_repeat = request.form['password_repeat']

        error = None
        if len(password) < 8:
            error = 'Das Passwort muss mindestens 8 Zeichen lang sein.'
        elif not re.search("[A-Z]", password):
            error = 'Das Passwort muss mindestens einen Großbuchstaben enthalten.'
        elif not re.search("[a-z]", password):
            error = 'Das Passwort muss mindestens einen Kleinbuchstaben enthalten.'
        elif re.match("^[^A-Za-z0-9].*|.*[^A-Za-z0-9]$", password) or not re.search("[^A-Za-z0-9]", password):
            error = 'Das Passwort muss mindestens ein Sonderzeichen enthalten, das nicht am Anfang oder Ende steht.'
        elif password != password_repeat:
            error = 'Passwörter stimmen nicht überein.'

        error = register_user(vorname, nachname, email, alter, bankinstitut, password)
        if error:
            return render_template('registrierung.html', error=error, vorname=vorname, nachname=nachname,
                                   email=email, alter=alter, bankinstitut=bankinstitut, passwort=password,
                                   passwort_repeat=password_repeat)

        return redirect(url_for('startseite'))
    return render_template('registrierung.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        result = login_user(email, password)
        if result:
            session['email'] = result[0]
            session['is_logged'] = True
            return redirect(url_for('profil_page'))
        else:
            return render_template("login.html", error="Passwort ist falsch oder Kunde existiert nicht",email=email)
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    name = logout_user(session.get('email'))
    session.pop('email', None)
    return render_template('logout_page.html', name=name)

@app.route('/profil_page', methods=['GET', 'POST'])
def profil_page():
    if request.method == 'POST':
        name = request.form.get('create_konto')
        email = session.get('email')
        print(name, email[0])
        create_konto = konto_anlegen(name, email[0])

        return render_template('profil_page.html',create_konto=create_konto)
    return render_template('profil_page.html')

@app.route('/kontoauszug_anlegen', methods=[ 'GET','POST'])
def kontoauszug_anlegen():
    zeitstempel = request.form.get('zeitstempel')
    betrag = request.form.get('betrag')
    empfaenger = request.form.get('empfaenger')
    verwendungszweck = request.form.get('verwendungszweck')

    return

if __name__ == '__main__':
    app.run()
