from flask import Blueprint, request, redirect, url_for
import hashlib

# Criação do blueprint para cadastro
cadastro_bp = Blueprint('cadastro', __name__)

# Simular um banco de dados simples
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

    return '''
        <form method="post">
            Usuário: <input type="text" name="username"><br>
            Senha: <input type="password" name="password"><br>
            <input type="submit" value="Cadastrar">
        </form>
    '''
