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
    return redirect(url_for('todos_gastos'))@gastos_bp.route('/excluir/<int:id>', methods=['POST'])
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



  
  
@gastos_bp.route('/pagar', methods=['POST'])
def pagar_gastos():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    gastos_selecionados = request.form.getlist('gastos_selecionados')
    
    if not gastos_selecionados:
        flash('Nenhum gasto selecionado para pagamento.', 'danger')
        return redirect(url_for('todos_gastos'))

    for gasto_id in gastos_selecionados:
        tipo_pagamento = request.form.get(f'tipo_pagamento_{gasto_id}')
        valor_pago_input = request.form.get(f'valor_pago_{gasto_id}', '0').replace('R$', '').replace('.', '').replace(',', '.')

        try:
            valor_pago = float(valor_pago_input)
        except ValueError:
            flash(f'O valor inserido para o gasto ID {gasto_id} é inválido.', 'danger')
            continue

        if tipo_pagamento == 'total':
            cursor.execute('UPDATE gastos SET pago = 1, valor_pago = valor WHERE id = ?', (gasto_id,))
        elif tipo_pagamento == 'parcial':
            cursor.execute('SELECT valor, valor_pago FROM gastos WHERE id = ?', (gasto_id,))
            valor_total, valor_pago_atual = cursor.fetchone()
            novo_valor_pago = valor_pago_atual + valor_pago

            cursor.execute('UPDATE gastos SET valor_pago = ? WHERE id = ?', (novo_valor_pago, gasto_id))
            cursor.execute('UPDATE gastos SET pago = CASE WHEN valor_pago >= valor THEN 1 ELSE 0 END WHERE id = ?', (gasto_id,))

    conn.commit()
    conn.close()
    flash('Pagamentos processados!', 'success')
    return redirect(url_for('todos_gastos'))