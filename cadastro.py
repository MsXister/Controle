from flask import Blueprint, request, redirect, url_for, render_template
import hashlib

# Blueprint do cadastro
cadastro_bp = Blueprint('cadastro', __name__)

usuarios = {}

@cadastro_bp.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in usuarios:
            return "Usuário já existe. Tente outro nome."
        
        usuarios[username] = hashed_password
        return redirect(url_for('login.login'))

    return render_template('cadastro.html')
