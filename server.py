import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from cadastro import cadastro_bp
from login import login_bp
from gastos import gastos_bp
from utils import verificar_ou_adicionar_colunas
from datetime import datetime
import sqlite3

# =========================================================
# 🔧 Configuração Inicial
# =========================================================

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

# =========================================================
# 🧪 Filtros personalizados Jinja2
# =========================================================

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

app.jinja_env.filters['formatar_valor'] = formatar_valor
app.jinja_env.filters['formatar_data'] = formatar_data
app.jinja_env.filters['formatar_data_mes'] = formatar_data_mes

# =========================================================
# 🗃️ Banco e Blueprints
# =========================================================

verificar_ou_adicionar_colunas()

app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(gastos_bp, url_prefix='/gastos')

# =========================================================
# 🌐 Rotas principais
# =========================================================

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
    return render_template(
        'dashboard.html',
        username=session['username'],
        gastos_recentes=gastos_recentes,
        resumo_categorias=resumo_categorias,
        todos_gastos=todos_gastos,
        is_admin=is_admin
    )

@app.route('/todos_gastos', methods=['GET', 'POST'])
def todos_gastos():
    if 'username' not in session:
        flash('Por favor, faça login para acessar os gastos.', 'warning')
        return redirect(url_for('login.login'))

    periodo = request.args.get('periodo', 'mes')
    mes_atual = request.args.get('mes', datetime.now().strftime('%Y-%m'))
    dia_atual = request.args.get('dia', datetime.now().strftime('%Y-%m-%d'))
    status = request.args.get('status', '')

    query = '''
        SELECT g.descricao, ROUND(g.valor, 2), g.data, g.categoria, u.username, g.id, g.pago, g.valor_pago
        FROM gastos g
        JOIN usuarios u ON g.usuario_id = u.id
        WHERE 1=1
    '''
    params = []

    if periodo == 'mes':
        query += " AND strftime('%Y-%m', g.data) = ?"
        params.append(mes_atual)
    elif periodo == 'dia':
        query += " AND g.data = ?"
        params.append(dia_atual)

    if status:
        query += " AND g.pago = ?"
        if status == 'pago':
            params.append(1)
        elif status == 'parcial':
            params.append(0)
            query += " AND g.valor_pago > 0"
        elif status == 'pendente':
            params.append(0)
            query += " AND g.valor_pago = 0"

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    todos_gastos = cursor.fetchall()
    conn.close()

    return render_template(
        'todos_gastos.html',
        mes_atual=mes_atual,
        dia_atual=dia_atual,
        todos_gastos=todos_gastos,
        year=datetime.now().year
    )

@app.route('/ver_resumo')
def ver_resumo():
    if 'username' not in session:
        flash('Por favor, faça login para acessar o resumo.', 'warning')
        return redirect(url_for('login.login'))

    return render_template('ver_resumo.html')

@app.route('/logout', endpoint='logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Você saiu da sua conta com sucesso.', 'success')
    return redirect(url_for('login.login'))

# =========================================================
# ▶️ Execução
# =========================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
