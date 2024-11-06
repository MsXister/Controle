from flask import Blueprint, request, redirect, url_for, render_template, session, flash
import hashlib
import sqlite3

login_bp = Blueprint('login', __name__)

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['is_admin'] = user[3]  # Verifica se é admin
            return redirect(url_for('dashboard'))
        else:
            flash("Usuário ou senha incorretos!", "error")  # Adiciona a mensagem de erro ao flash

    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    session.clear()  # Limpa toda a sessão
    return redirect(url_for('login.login'))  # Redireciona para a página de login