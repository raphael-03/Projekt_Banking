from flask import Flask,flash, Response, render_template, request, redirect, url_for, session
import re
import hashlib
import pandas as pd
from DB_code import register_user, login_user, logout_user, konto_anlegen, konto_anzeigen, create_kontoauszug_anlegen, finde_kontoid_durch_namen, letzten_kontoeintraege_zeigen,letzten_kontoeintraege_zeigen_5, pruefe_konto
from DB_code import kategorien_waehlen, kategorien_erstellen_2, finde_kontoid_name_email, ergebnis_suchfunktion, excel_export, insert_into_database
app = Flask(__name__)
app.secret_key = 'AhmetundRaphael'

# Benutzerregistrierung und -anmeldung
@app.route('/', methods=['GET', 'POST'])
def startseite():
    return render_template("startseite.html")

# Erstellt einen SHA256 Hash des Passworts
def hash_password(password):

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed_password

@app.route('/registrierung', methods=['GET', 'POST'])
def registrierung():
    if request.method == 'POST':
        # Extrahiere Formulardaten
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        email = request.form.get('email')
        alter = request.form.get('alter')
        bankinstitut = request.form.get('bankinstitut')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        # Einfache Passwort-Validierung
        error = None
        if password != password_repeat:
            error = 'Passwörter stimmen nicht überein.'

        if error:
            return render_template('registrierung.html', error=error)
        else:
            # Hash das Passwort
            hashed_password = hash_password(password)
            # Speichere den Benutzer mit dem gehashten Passwort
            register_user(vorname, nachname, email, alter, bankinstitut, hashed_password)
            return redirect(url_for('startseite'))

    return render_template('registrierung.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_tuple_list = login_user(email)
        if user_tuple_list:
            user = {'email': user_tuple_list[0][0], 'hashed_password': user_tuple_list[0][1]}
            print(user)
            provided_password_hash = hash_password(password)

            if provided_password_hash == user['hashed_password']:
                session['email'] = user['email']
                print(user['email'])
                session['is_logged_in'] = True
                print('Logged in successfully!')
                return redirect(url_for('profil_page'))
            else:
                return render_template("login.html", error="Passwort ist falsch oder Benutzer existiert nicht", email=email)
        else:
            return render_template("login.html", error="Passwort ist falsch oder Benutzer existiert nicht", email=email)
    return render_template('login.html')
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print(session.get('email'))
    vorname = logout_user(session.get('email'))[0]
    session.pop('email', None)
    session.pop('is_logged_in', None)
    return render_template('logout_page.html', vorname=vorname)

#Dies ist hier die Übersicht nach dem Login
@app.route('/profil_page', methods=['GET', 'POST'])
def profil_page():
    email = session.get('email')
    eintrag = letzten_kontoeintraege_zeigen_5(email)
    konto_pruefen = pruefe_konto(email)
    anzahl = True

    return render_template('profil_page.html', eintrag=eintrag, konto_pruefen=konto_pruefen, email=email, anzahl=anzahl)

@app.route('/konto_uebersicht/<name>', methods=['GET', 'POST'])
def konto_uebersicht(name):
    email = session.get('email')
    kontid = finde_kontoid_name_email(email, name)[0]
    anzahl_eintraege = request.args.get('anzahl_eintraege', default=15, type=int)
    eintrag = letzten_kontoeintraege_zeigen(email, kontid, anzahl_eintraege)

    return render_template('konto_uebersicht.html', email=email, eintrag=eintrag, name=name, kontoid=kontid, anzahl_eintraege=anzahl_eintraege)


@app.route('/konto_anzeigen', methods=['GET', 'POST'])
def kontos_anzeigen():
    email = session.get('email')
    konto_anzeige = konto_anzeigen(email)
    return render_template('kontos_anzeigen.html', konto_anzeige=konto_anzeige)

# Funktion um ein Konto zu erstellen
@app.route('/konto_erstellen', methods=['GET','POST'])
def konto_erstellen():
    if request.method == 'POST':
        name = request.form.get('create_konto')
        email = session.get('email')
        konto_anlegen(name, email )
        return redirect(url_for('kontos_anzeigen', email=email))
    return render_template('create_konto.html')

@app.route('/konto_waehlen/<name>')
def konto_waehlen(name):
    email = session.get('email')
    kontoid = finde_kontoid_durch_namen(name, email)
    if kontoid is not None:
        return redirect(url_for('kontoauszug_anlegen', kontoid=kontoid))
    else:
        return "Konto nicht gefunden", 404

# Funtkion um ein Eintrag zu erstellen
@app.route('/kontoauszug_anlegen/<kontoid>/<name>', methods=[ 'GET','POST'])
def kontoauszug_anlegen(kontoid, name):
    print(f"Route aufgerufen mit kontoid: {kontoid}")
    if request.method == 'POST':
        email = session.get('email')
        zeitstempel = request.form.get('zeitstempel')
        betrag = request.form.get('betrag')
        empfaenger = request.form.get('empfaenger')
        verwendungszweck = request.form.get('verwendungszweck')
        create_kontoauszug_anlegen(zeitstempel, betrag, empfaenger, verwendungszweck, email, kontoid)
        return redirect(url_for('konto_uebersicht', kontoid=kontoid, name=name))
    return render_template('create_kontoeintrag.html', kontoid=kontoid, name=name)

#Klassifikation von Kontoeintraegen
@app.route('/kategorien_anlegen/<email>', methods=[ 'GET','POST'])
def kategorien_anlegen(email):
    if request.method == 'POST':
        name = request.form.get('k_name')
        schlagwoerter = request.form.get('schlagwoerter')
        kategorien_erstellen_2(email, name, schlagwoerter)
        return redirect(url_for('kategorien_uebersicht',email=email, schlagwoerter=schlagwoerter))
    return render_template('kategorien_anlegen.html', email=email)

@app.route('/kategorien_uebersicht/<email>', methods=[ 'GET','POST'])
def kategorien_uebersicht(email):
    kategoriebezeichnung = kategorien_waehlen(email)
    return render_template('kategorie_uebersicht.html', kategoriebezeichnung=kategoriebezeichnung, email=email)

#Suchfunktionen

@app.route('/suchfunktionen_formular/<kontoid>', methods=['GET', 'POST'])
def suchfunktionen_formular(kontoid):
    print(f"kontoid: {kontoid}")
    email = session.get('email')
    if request.method == 'POST':
        stichwort = request.form.get('stichwort')
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')
        betrag = request.form.get('betrag')
        empfaenger = request.form.get('empfaenger')
        suchfunktion_ausgabe = ergebnis_suchfunktion(email[0], kontoid, stichwort, startDate, endDate, betrag, empfaenger)
        print(f"Route{suchfunktion_ausgabe[0]}")
        ergebnis_summe = suchfunktion_ausgabe[1][0][0]
        return render_template('suchfunktionen_formular.html',email=email, kontoid=kontoid, suchfunktion_ausgabe=suchfunktion_ausgabe[0], ergebnis_summe=ergebnis_summe)
    return render_template('suchfunktionen_formular.html',email=email, kontoid=kontoid)

@app.route('/ausfuehrung_export/<kontoid>', methods = ['GET', 'POST'])
def ausfuehrung_export(kontoid):
    email = session.get('email')
    excel_file = excel_export(email,kontoid)
    return Response(excel_file.getvalue(),mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={"Content-Disposition": f"attachment;filename=Kontoeintraege_{kontoid}.xlsx"})

# import der excel datei
@app.route('/upload_excel/<name>/<kontoid>', methods=['GET', 'POST'])
def upload_excel(name, kontoid):
    email = session.get('email')
    print(f"Uploading Excel")
    if request.method == 'POST':
        if 'excel_file' not in request.files:
            flash('Keine Datei Teil der Anfrage')
            return redirect(url_for('konto_uebersicht', name=name, kontoid=kontoid, email=email))
        file = request.files['excel_file']
        if file.filename == '':
            flash('Keine ausgewählte Datei')
            return redirect(url_for('konto_uebersicht', name=name, kontoid=kontoid, email=email))
        if file and allowed_file(file.filename):
            # Nur bestimmte Spalten aus der Excel-Datei lesen
            df = pd.read_excel(file, usecols=['Zeitstempel', 'Betrag', 'Empfaenger', 'Verwendungszweck'])
            # Daten in die Datenbank einfügen
            insert_into_database(df,email, kontoid)

            flash('Datei erfolgreich hochgeladen und in die Datenbank eingefügt')
            return redirect(url_for('konto_uebersicht', name=name, kontoid=kontoid, email=email))
        else:
            return redirect(url_for('konto_uebersicht', name=name, kontoid=kontoid, email=email))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx'}


if __name__ == '__main__':
    app.run()
