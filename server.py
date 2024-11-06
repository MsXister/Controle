from flask import Flask, redirect, url_for
from cadastro import cadastro_bp
from login import login_bp

app = Flask(__name__)

# Registrar os blueprints
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')

# Redirecionar para login na rota inicial
@app.route('/')
def home():
    return redirect(url_for('login.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
