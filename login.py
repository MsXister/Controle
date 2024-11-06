from flask import Blueprint, request, redirect, url_for, render_template, session
import hashlib  # Para criptografar as senhas

login_bp = Blueprint('login', __name__)

from cadastro import usuarios  # Importa o dicionário de usuários do módulo cadastro

# Rota de login
@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Processa o formulário de login
        username = request.form['username']  # Obtém o nome de usuário
        password = request.form['password']  # Obtém a senha
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Criptografa a senha

        # Verifica se o usuário e a senha estão corretos
        if username in usuarios and usuarios[username] == hashed_password:
            session['username'] = username  # Armazena o usuário na sessão
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard
        else:
            return "Usuário ou senha incorretos!"  # Mensagem de erro se as credenciais forem inválidas

    return render_template('login.html')  # Renderiza a página de login

# Rota de logout
@login_bp.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    return redirect(url_for('login.login'))  # Redireciona para a página de login
