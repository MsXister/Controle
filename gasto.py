from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3

gastos_bp = Blueprint('gastos', __name__)

@gastos_bp.route('/gastos/adicionar', methods=['GET', 'POST'])
def adicionar_gasto():
    if 'username' not in session:
        flash('Você precisa estar logado para adicionar gastos.', 'warning')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        valor = request.form['valor']
        data = request.form['data']
        
        # Obter o ID do usuário logado
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (session['username'],))
        usuario_id = cursor.fetchone()[0]

        # Inserir o novo gasto
        cursor.execute('INSERT INTO gastos (descricao, categoria, valor, data, usuario_id) VALUES (?, ?, ?, ?, ?)',
                       (descricao, categoria, valor, data, usuario_id))
        conn.commit()
        conn.close()

        flash('Gasto adicionado com sucesso!', 'success')
        return redirect(url_for('gastos.listar_gastos'))

    return render_template('adicionar_gasto.html')
