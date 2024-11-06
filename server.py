from flask import Flask, redirect, url_for, session, render_template
from cadastro import cadastro_bp
from login import login_bp

app = Flask(__name__)

# Configuração de uma chave secreta para gerenciar sessões
app.secret_key = 'sua_chave_secreta_aleatoria'

# Registrar os blueprints para dividir funcionalidades de cadastro e login
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')

# Rota principal: redireciona para o dashboard se o usuário estiver logado, caso contrário, vai para login
@app.route('/')
def home():
    if 'username' in session:  # Verifica se o usuário está logado
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard
    return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado

# Rota do dashboard: exibe informações do usuário logado
@app.route('/dashboard')
def dashboard():
    if 'username' in session:  # Verifica se o usuário está logado
        return render_template('dashboard.html', username=session['username'])  # Renderiza o dashboard
    return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)  # Inicia o servidor na porta 3000
