
from uuid import uuid4
import string
import random
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask.wrappers import Response
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def gerador_senha():
    tamanho = 10
    min = string.ascii_lowercase
    max = string.ascii_uppercase
    num = string.digits
    sym = '!@#$%&*()'
    senha = ''.join(random.sample(min+max+sym+num, tamanho))
    return senha

def get_data(link):
    conn = get_db_connection()
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    conn.row_factory = dict_factory
    cur = conn.cursor()
    data = cur.execute('SELECT * FROM senhas WHERE url_link = ?', 
                        (link,)).fetchone()
    conn.close()
    if data is None:
        abort(404)
        
    return data

def counter(link):

    conn = get_db_connection()
    conn.execute('UPDATE senhas SET Acessos_realizados = Acessos_realizados + 1 WHERE url_link = ?',
                (link,)).fetchone()
    conn.commit()
    conn.close()

def delete_acessos(link):
    conn = get_db_connection()
    for row in conn.execute('SELECT Acessos_realizados FROM senhas WHERE url_link = ?', (link,)):
        nacessos = row[0]

    for row in conn.execute('SELECT Acessos_disponiveis FROM senhas WHERE url_link = ?', (link,)):
        acessos = row[0]

        if acessos <= nacessos:
            conn.execute('DELETE FROM senhas WHERE url_link = ?', (link,))
    
    conn.commit()
    conn.close()

def delete_tempo(link):
    conn = get_db_connection()
    for row in conn.execute('SELECT Data_criacao FROM senhas WHERE url_link = ?', (link,)):
        criacao = row[0]

    for row in conn.execute('SELECT Data_expiracao FROM senhas WHERE url_link = ?', (link,)):
        expire = row[0]
        if criacao >= expire:
            abort(Response('Data de criação não pode ser menor que a data Atual!'))

        if expire < criacao:
            conn.execute('DELETE FROM senhas WHERE url_link = ?', (link,))
    
    conn.commit()
    conn.close()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/gerar', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        acessos = request.form['Acessos_disponiveis']
        tempo = request.form['Data_expiracao']
        senha = gerador_senha()
        endereco = str(uuid4())
        nacessos = 0
    
        conn = get_db_connection()
        conn.execute('INSERT INTO senhas (Acessos_disponiveis, Data_expiracao, senha, url_link, Acessos_realizados ) VALUES (?, ?, ?, ?, ?)',
                        (acessos, tempo, senha, endereco, nacessos))
        conn.commit()
        conn.close()
        return redirect(url_for('.url', url = endereco))

    return render_template('gerar.html')

@app.route('/url<string:url>')
def url(url):
    return render_template('url.html', link = url)

@app.route('/<string:link>')
def display_password(link):
    counter(link)
    data = get_data(link)
    delete_acessos(link)
    delete_tempo(link)
    return render_template('data.html', data = data)
    


