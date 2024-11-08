from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3

gastos_bp = Blueprint('gastos', __name__)  # Definindo o Blueprint

@gastos_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_gasto():
    if 'username' not in session:
        flash('Por favor, faça login para adicionar gastos.', 'warning')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        valor = request.form['valor']
        data = request.form['data']

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (session['username'],))
        usuario_id = cursor.fetchone()[0]

        cursor.execute('INSERT INTO gastos (descricao, categoria, valor, data, usuario_id) VALUES (?, ?, ?, ?, ?)',
                       (descricao, categoria, valor, data, usuario_id))
        conn.commit()
        conn.close()

        flash('Gasto adicionado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('adicionar_gasto.html')
  

@gastos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_gasto(id):
    if 'username' not in session:
        flash('Por favor, faça login para editar gastos.', 'warning')
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        valor = request.form['valor']
        data = request.form['data']

        cursor.execute('''
            UPDATE gastos
            SET descricao = ?, categoria = ?, valor = ?, data = ?
            WHERE id = ?
        ''', (descricao, categoria, valor, data, id))
        conn.commit()
        flash('Gasto atualizado com sucesso!', 'success')
        return redirect(url_for('todos_gastos'))

    cursor.execute('SELECT * FROM gastos WHERE id = ?', (id,))
    gasto = cursor.fetchone()
    conn.close()

    return render_template('editar_gasto.html', gasto=gasto)


@gastos_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir_gasto(id):
    if 'username' not in session:
        flash('Por favor, faça login para excluir gastos.', 'warning')
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gastos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Gasto excluído com sucesso!', 'success')
    return redirect(url_for('todos_gastos'))
