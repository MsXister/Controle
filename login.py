from flask import Blueprint, request, redirect, url_for, render_template, session
import hashlib
import sqlite3

login_bp = Blueprint('login', __name__)

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Conectar ao banco de dados e verificar as credenciais
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['is_admin'] = user[3]  # Verifica se o usuário é admin
            return redirect(url_for('dashboard'))
        else:
            return "Usuário ou senha incorretos!"

    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))
