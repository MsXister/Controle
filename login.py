from flask import Blueprint, request

# Criação do blueprint para login
login_bp = Blueprint('login', __name__)

# Importar o dicionário de usuários de cadastro
from cadastro import usuarios
import hashlib

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Criptografar a senha
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in usuarios and usuarios[username] == hashed_password:
            return "Login bem-sucedido! Bem-vindo, " + username
        else:
            return "Usuário ou senha incorretos!"

    return '''
        <form method="post">
            Usuário: <input type="text" name="username"><br>
            Senha: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''
