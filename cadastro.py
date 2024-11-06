from flask import Blueprint, request, redirect, url_for, render_template
import hashlib
import sqlite3

cadastro_bp = Blueprint('cadastro', __name__)

@cadastro_bp.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Usuário já existe! Tente outro nome."
        finally:
            conn.close()

        return redirect(url_for('login.login'))

    return render_template('cadastro.html')
