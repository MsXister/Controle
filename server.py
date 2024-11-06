from flask import Flask
from cadastro import cadastro_bp
from login import login_bp

app = Flask(__name__)

# Registrar os blueprints (módulos separados)
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')

@app.route('/')
def home():
    return "Bem-vindo ao Controle de Gastos!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
