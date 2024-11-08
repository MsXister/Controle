from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from cadastro import cadastro_bp
from login import login_bp
import sqlite3
from utils import verificar_ou_adicionar_colunas  # Importar a função
from gastos import gastos_bp
from datetime import datetime

app = Flask(__name__)

# Defina uma chave secreta para gerenciar as sessões
app.secret_key = 'uma_chave_secreta_segura'

# Filtros personalizados
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data):
    try:
        return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data

def formatar_data_mes(data):
    try:
        return datetime.strptime(data, "%Y-%m").strftime("%B %Y")
    except ValueError:
        return data

# Registrar os filtros no Jinja
app.jinja_env.filters['formatar_valor'] = formatar_valor
app.jinja_env.filters['formatar_data'] = formatar_data
app.jinja_env.filters['formatar_data_mes'] = formatar_data_mes

# Verificar colunas no banco de dados
verificar_ou_adicionar_colunas()

# Registrar os blueprints
app.register_blueprint(gastos_bp, url_prefix='/gastos')
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')

# Rotas principais
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login.login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Por favor, faça login para acessar o dashboard.', 'warning')
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, is_admin FROM usuarios WHERE username = ?', (session['username'],))
    resultado = cursor.fetchone()

    if resultado:
        usuario_id, is_admin = resultado
        cursor.execute('''SELECT descricao, ROUND(valor, 2), data 
                          FROM gastos 
                          WHERE usuario_id = ? 
                          ORDER BY data DESC LIMIT 5''', (usuario_id,))
        gastos_recentes = cursor.fetchall()

        cursor.execute('''SELECT categoria, ROUND(SUM(valor), 2) 
                          FROM gastos 
                          WHERE usuario_id = ? GROUP BY categoria''', (usuario_id,))
        resumo_categorias = cursor.fetchall()

        cursor.execute('''SELECT g.descricao, ROUND(g.valor, 2), g.data, g.categoria, u.username
                          FROM gastos g
                          JOIN usuarios u ON g.usuario_id = u.id
                          ORDER BY g.data DESC''')
        todos_gastos = cursor.fetchall()
    else:
        gastos_recentes, resumo_categorias, todos_gastos, is_admin = [], [], [], False

    conn.close()
    return render_template('dashboard.html', username=session['username'], gastos_recentes=gastos_recentes, 
                           resumo_categorias=resumo_categorias, todos_gastos=todos_gastos, is_admin=is_admin)

@app.route('/todos_gastos', methods=['GET', 'POST'])
def todos_gastos():
    if 'username' not in session:
        flash('Por favor, faça login para acessar os gastos.', 'warning')
        return redirect(url_for('login.login'))

    mes_atual = request.args.get('mes', datetime.now().strftime('%Y-%m'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Garantir que valores nulos sejam tratados corretamente
    cursor.execute('''
        SELECT 
            g.descricao, 
            ROUND(g.valor, 2), 
            g.data, 
            g.categoria, 
            u.username, 
            g.id, 
            g.pago, 
            COALESCE(g.valor_pago, 0) -- Tratamento de nulos
        FROM gastos g
        JOIN usuarios u ON g.usuario_id = u.id
        WHERE strftime('%Y-%m', g.data) = ?
    ''', (mes_atual,))
    todos_gastos = cursor.fetchall()
    conn.close()

    return render_template('todos_gastos.html', mes_atual=mes_atual, todos_gastos=todos_gastos, year=datetime.now().year)
  
  
  
# Rota para logout com um endpoint definido corretamente
@app.route('/logout', endpoint='logout')
def logout():
    # Remove a sessão do usuário
    session.pop('username', None)
    session.pop('is_admin', None)  # Remove também o status de admin
    flash('Você saiu da sua conta com sucesso.', 'success')
    return redirect(url_for('login.login'))
  
  
@app.route('/gastos/pagar', methods=['POST'])
def pagar_gastos():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    for gasto_id in request.form.getlist('gastos_selecionados'):
        tipo_pagamento = request.form.get(f'tipo_pagamento_{gasto_id}')
        valor_pago_input = request.form.get(f'valor_pago_{gasto_id}', '0').replace('R$', '').replace('.', '').replace(',', '.')

        try:
            valor_pago = float(valor_pago_input)
        except ValueError:
            valor_pago = 0.0

        if tipo_pagamento == 'total':
            # Marca o gasto como totalmente pago
            cursor.execute('UPDATE gastos SET pago = 1, valor_pago = valor WHERE id = ?', (gasto_id,))
        elif tipo_pagamento == 'parcial':
            # Atualiza o valor pago parcialmente
            cursor.execute('UPDATE gastos SET valor_pago = valor_pago + ? WHERE id = ?', (valor_pago, gasto_id))
            # Atualiza o status para pago se o valor total já foi quitado
            cursor.execute('UPDATE gastos SET pago = CASE WHEN valor_pago >= valor THEN 1 ELSE 0 END WHERE id = ?', (gasto_id,))

    conn.commit()
    conn.close()
    flash('Pagamentos atualizados com sucesso!', 'success')
    return redirect(url_for('todos_gastos'))

  
  
  
@app.route('/gastos/excluir/<int:id>', methods=['GET', 'POST'])
def excluir(id):
    if 'username' not in session:
        flash('Por favor, faça login para continuar.', 'warning')
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gastos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Gasto excluído com sucesso!', 'success')
    return redirect(url_for('todos_gastos'))

  
@app.route('/gastos/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'username' not in session:
        flash('Por favor, faça login para continuar.', 'warning')
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = request.form['valor']
        data = request.form['data']
        categoria = request.form['categoria']

        cursor.execute('''
            UPDATE gastos
            SET descricao = ?, valor = ?, data = ?, categoria = ?
            WHERE id = ?
        ''', (descricao, valor, data, categoria, id))
        conn.commit()
        conn.close()

        flash('Gasto atualizado com sucesso!', 'success')
        return redirect(url_for('todos_gastos'))
    
    cursor.execute('SELECT descricao, valor, data, categoria FROM gastos WHERE id = ?', (id,))
    gasto = cursor.fetchone()
    conn.close()

    return render_template('editar_gasto.html', gasto=gasto, id=id)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
