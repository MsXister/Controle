from flask import Blueprint, request, render_template
import hashlib

# Criação do blueprint para login
login_bp = Blueprint('login', __name__)

# Importar o dicionário de usuários do cadastro
from cadastro import usuarios

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Criptografar a senha para comparação
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in usuarios and usuarios[username] == hashed_password:
            return f"Login bem-sucedido! Bem-vindo, {username}."
        else:
            return "Usuário ou senha incorretos!"

    # Renderiza o formulário de login
    return render_template('login.html')
