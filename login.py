from flask import Blueprint, request, redirect, url_for, render_template, session
import hashlib

login_bp = Blueprint('login', __name__)

# Importar o dicionário de usuários do cadastro
from cadastro import usuarios

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in usuarios and usuarios[username] == hashed_password:
            # Salvar o usuário na sessão
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Usuário ou senha incorretos!"

    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    # Limpar a sessão
    session.pop('username', None)
    return redirect(url_for('login.login'))
