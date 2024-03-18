from flask import Flask,flash, Response, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import hashlib, io
import base64
import pandas as pd
from DB_code import register_user, login_user, logout_user, konto_anlegen, konto_anzeigen, create_kontoauszug_anlegen, finde_kontoid_durch_namen, letzten_kontoeintraege_zeigen,letzten_kontoeintraege_zeigen_5, pruefe_konto
from DB_code import kategorien_waehlen, kategorien_erstellen_2, finde_kontoid_name_email, ergebnis_suchfunktion, excel_export, insert_into_database, sortieren_nach_kategorien, finde_konto_name
app = Flask(__name__)
app.secret_key = 'AhmetundRaphael'

@app.route('/', methods=['GET', 'POST'])
def startseite():
    return render_template("startseite.html")

# Erstellt einen SHA256 Hash des Passworts
#Ahmet
def hash_password(password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed_password
#Ahmet
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

#ahmet
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

#ahmet
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print(session.get('email'))
    vorname = logout_user(session.get('email'))[0]
    session.pop('email', None)
    session.pop('is_logged_in', None)
    return render_template('logout_page.html', vorname=vorname)

#Dies ist hier die Übersicht nach dem Login
#Raphael
@app.route('/profil_page', methods=['GET', 'POST'])
def profil_page():
    email = session.get('email')
    eintrag = letzten_kontoeintraege_zeigen_5(email)
    konto_pruefen = pruefe_konto(email)
    anzahl = True
    return render_template('profil_page.html', eintrag=eintrag, konto_pruefen=konto_pruefen, email=email, anzahl=anzahl)

#Raphael
@app.route('/konto_uebersicht/<name>', methods=['GET', 'POST'])
def konto_uebersicht(name):
    email = session.get('email')
    kontid = finde_kontoid_name_email(email, name)[0]
    anzahl_eintraege = request.args.get('anzahl_eintraege', default=15, type=int)
    eintrag = letzten_kontoeintraege_zeigen(email, kontid, anzahl_eintraege)
    return render_template('konto_uebersicht.html', email=email, eintrag=eintrag, name=name, kontoid=kontid, anzahl_eintraege=anzahl_eintraege)

#ahmet
@app.route('/konto_anzeigen', methods=['GET', 'POST'])
def kontos_anzeigen():
    email = session.get('email')
    konto_anzeige = konto_anzeigen(email)
    return render_template('kontos_anzeigen.html', konto_anzeige=konto_anzeige)

# Funktion um ein Konto zu erstellen
#ahmet
@app.route('/konto_erstellen', methods=['GET','POST'])
def konto_erstellen():
    if request.method == 'POST':
        name = request.form.get('create_konto')
        email = session.get('email')
        konto_anlegen(name, email )
        return redirect(url_for('kontos_anzeigen', email=email))
    return render_template('create_konto.html')

#ahmet
@app.route('/konto_waehlen/<name>')
def konto_waehlen(name):
    email = session.get('email')
    kontoid = finde_kontoid_durch_namen(name, email)
    if kontoid is not None:
        return redirect(url_for('kontoauszug_anlegen', kontoid=kontoid))
    else:
        return "Konto nicht gefunden", 404

# Funtkion um ein Eintrag zu erstellen
#Raphael
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
#ahmet
@app.route('/kategorien_anlegen/<email>', methods=[ 'GET','POST'])
def kategorien_anlegen(email):
    if request.method == 'POST':
        name = request.form.get('k_name')
        schlagwoerter = request.form.get('schlagwoerter')
        kategorien_erstellen_2(email, name, schlagwoerter)
        return redirect(url_for('kategorien_uebersicht',email=email, schlagwoerter=schlagwoerter))
    return render_template('kategorien_anlegen.html', email=email)

#ahmet
@app.route('/kategorien_uebersicht/<email>', methods=[ 'GET','POST'])
def kategorien_uebersicht(email):
    kategoriebezeichnung = kategorien_waehlen(email)
    return render_template('kategorie_uebersicht.html', kategoriebezeichnung=kategoriebezeichnung, email=email)

#Suchfunktionen
#Raphael
@app.route('/suchfunktionen_formular/<kontoid>', methods=['GET', 'POST'])
def suchfunktionen_formular(kontoid):

    email = session.get('email')
    if request.method == 'POST':
        stichwort = request.form.get('stichwort')
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')
        betrag = request.form.get('betrag')
        empfaenger = request.form.get('empfaenger')

        suchfunktion_ausgabe = ergebnis_suchfunktion(email, kontoid, stichwort, startDate, endDate, betrag, empfaenger)

        ergebnis_summe = suchfunktion_ausgabe[1][0][0]
        return render_template('suchfunktionen_formular.html',email=email, kontoid=kontoid, suchfunktion_ausgabe=suchfunktion_ausgabe[0], ergebnis_summe=ergebnis_summe)
    return render_template('suchfunktionen_formular.html',email=email, kontoid=kontoid)

#export der einträge
#Ahmet und Raphael
@app.route('/ausfuehrung_export/<kontoid>', methods=['GET', 'POST'])
def ausfuehrung_export(kontoid):
    email = session.get('email')
    excel_file = excel_export(email,kontoid)
    return Response(excel_file.getvalue(),mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={"Content-Disposition": f"attachment;filename=Kontoeintraege_{kontoid}.xlsx"})

# import der excel datei
#Ahmet und Raphael
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

            insert_into_database(df,email, kontoid)

            flash('Datei erfolgreich hochgeladen und in die Datenbank eingefügt')
            return redirect(url_for('konto_uebersicht', name=name, kontoid=kontoid, email=email))
        else:
            return redirect(url_for('konto_uebersicht', name=name, kontoid=kontoid, email=email))

#ahmet und Raphael
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx'}

#Kontoeinträge Visuell darstellen
#Raphael
@app.route('/visualisierung_konto_eintraege/<email>/<kontoid>', methods=['GET', 'POST'])
def visualisierung_konto_eintraege(email, kontoid):
    name = finde_konto_name(email, kontoid)
    if request.method == 'POST':
        jahr = request.form.get('jahr')
        monat = request.form.get('monat')
        start_datum = request.form.get('start_datum')
        ende_datum = request.form.get('ende_datum')
        return redirect(
            url_for('visualisierung_konto_eintraege', email=email, kontoid=kontoid, **request.args, jahr=jahr,
                    monat=monat, start_datum=start_datum, ende_datum=ende_datum, name=name))

    jahr = request.args.get('jahr')
    monat = request.args.get('monat')
    start_datum = request.args.get('start_datum')
    ende_datum = request.args.get('ende_datum')

    eintraege = sortieren_nach_kategorien(email, kontoid, jahr=jahr, monat=monat, start_datum=start_datum, ende_datum=ende_datum)
    kategorisierte_eintraege = {}
    gesamtsummen = {}

    # Kategorisierte Einträge sammeln und Summen berechnen
    for eintrag in eintraege:
        kategorie = eintrag[0]
        if kategorie not in kategorisierte_eintraege:
            kategorisierte_eintraege[kategorie] = []
            gesamtsummen[kategorie] = 0
        kategorisierte_eintraege[kategorie].append(eintrag[1:])
        gesamtsummen[kategorie] += eintrag[2]

    # Kreisdiagramm für Kategoriesummen erstellen
    labels = gesamtsummen.keys()
    sizes = gesamtsummen.values()

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    # Diagramm in einen BytesIO-Stream speichern
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_url = 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('visualisierung_konto_eintraege.html', kategorisierte_eintraege=kategorisierte_eintraege, email=email, img_url=img_url, kontoid=kontoid, name=name)

if __name__ == '__main__':
    app.run()
