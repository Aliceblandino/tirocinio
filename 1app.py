from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from collections import Counter
from parser import parse_appello

app = Flask(__name__)
app.secret_key = "supersecret"  # serve per usare flash()

# cartella di upload
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# estensioni consentite
estensioni = ['csv', 'xls', 'xlsx']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in estensioni
#funzione per leggere il file
def leggi_file(filepath):
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath, sep=';')  # separatore tipico di Esse3
    elif filepath.endswith('.xls'):
        df = pd.read_excel(filepath, engine='xlrd')
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, engine='openpyxl')
    else:
        df = None
    return df


# -- home
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # login finto
        if email == '' or password == '':
            return render_template('index.html', error='Inserisci email e password')
        elif email == 'spes' and password == 'spes':
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error='Email o password errati')
    return render_template('index.html')

# dashboard
@app.route('/dashboard')
def dashboard():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if files:
        last_file = os.path.join(app.config['UPLOAD_FOLDER'], files[-1])
        df = leggi_file(last_file)
        if df is not None and not df.empty:
            # Mostra le colonne disponibili
            colonne = list(df.columns)

            n_studenti = len(df)

            media_voti = None
            if 'Esito' in df.columns:
                voti = df['Esito'].dropna().astype(str).str.extract(r'(\d+)').dropna().astype(int)
                media_voti = voti.mean()

            return render_template('dashboard.html',
                                   n_studenti=n_studenti,
                                   media_voti=media_voti,
                                   colonne=colonne)
    return render_template('dashboard.html', n_studenti=None, media_voti=None, colonne=None)

# upload
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nessun file selezionato')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nessun file selezionato')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            flash('File caricato con successo')
            return redirect(url_for('dashboard'))  # <-- questo è il redirect

            # Leggi il file con pandas
            df = leggi_file(filepath)
            if df is not None:
                # esempio: calcola numero righe e colonne
                n_righe, n_colonne = df.shape
                flash(f'File caricato con successo. Righe: {n_righe}, Colonne: {n_colonne}')
                # puoi anche salvare df in una variabile globale o sessione
                return redirect(url_for('dashboard'))
            else:
                flash('Formato non riconosciuto')
                return redirect(url_for('upload'))
        else:
            flash('Estensione non consentita')
            return render_template('request.html')
    return render_template('upload.html')



if __name__ == '__main__':
    app.run(debug=True)