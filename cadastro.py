import re
from flask import Blueprint, request, redirect, url_for, render_template
import hashlib
import sqlite3

cadastro_bp = Blueprint('cadastro', __name__)

# Função para validar o formato do username
def validar_username(username):
    return re.match(r'^[a-zA-Z]+\.[a-zA-Z]+$', username)

# Função para validar o formato da senha
def validar_senha(senha):
    return re.match(r'^(?=.*[A-Z])(?=.*[@$!%*?&])(?=.*[0-9]).{8,}$', senha)

@cadastro_bp.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validação do username
        if not validar_username(username):
            return "O nome de usuário deve estar no formato nome.sobrenome", 400

        # Validação da senha
        if not validar_senha(password):
            return "A senha deve ter pelo menos 1 letra maiúscula, 1 número, 1 caractere especial e 8 caracteres no total.", 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Usuário já existe! Tente outro nome.", 400
        finally:
            conn.close()

        return redirect(url_for('login.login'))

    # Sempre retorna a página de cadastro para requisições GET
    return render_template('cadastro.html')
