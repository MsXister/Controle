from flask import Blueprint, request, redirect, url_for, render_template
import hashlib

# Criação do blueprint para cadastro
cadastro_bp = Blueprint('cadastro', __name__)

# Simulação de um banco de dados simples
usuarios = {}

@cadastro_bp.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Criptografar a senha
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in usuarios:
            return "Usuário já existe! Tente outro nome."

        # Armazenar o usuário
        usuarios[username] = hashed_password
        return redirect(url_for('login.login'))

    # Renderiza o formulário de cadastro
    return render_template('cadastro.html')
