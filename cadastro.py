from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import re
import hashlib                         # mantido para não remover linhas existentes
from werkzeug.security import generate_password_hash  # novo import

cadastro_bp = Blueprint('cadastro', __name__, template_folder='templates')


@cadastro_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # validação de senha: 8+ caracteres, 1 maiúscula, 1 número, 1 caractere especial
        regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
        if not re.match(regex, password):
            flash('Senha deve conter pelo menos 8 caracteres, 1 maiúscula, 1 número e 1 caractere especial.')
            return redirect(url_for('cadastro.cadastro'))

        # hashed_password = hashlib.sha256(password.encode()).hexdigest()  # linha antiga (apenas comentada)
        hashed_password = generate_password_hash(password)               # linha nova compatível com login

        conn = sqlite3.connect('usuarios.db')
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            flash('Usuário cadastrado com sucesso!')
            return redirect(url_for('login.login'))
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe.')
            return redirect(url_for('cadastro.cadastro'))
        finally:
            conn.close()

    return render_template('cadastro.html')
