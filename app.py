# app.py
import os
from flask import Flask
from dotenv import load_dotenv

# Importe o 'db' do nosso novo arquivo 'extensions.py'
from extensions import db

def create_app():
    """
    Usa o padrão Factory para criar a aplicação Flask.
    """
    app = Flask(__name__)
    load_dotenv() # Carrega as variáveis do .env

    # --- Configuração do Banco de Dados ---
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("ERRO: DATABASE_URL não foi encontrada no arquivo .env")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Configuração da Chave Secreta (para Sessões) ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError("ERRO: SECRET_KEY não foi encontrada no arquivo .env")

    # Conecta a instância 'db' (de extensions.py) com o app Flask
    db.init_app(app)

    # --- Importação de Modelos e Rotas ---
    # Importamos os modelos AQUI, dentro do contexto,
    # para garantir que o 'db' já esteja configurado.
    from models import Cliente, Endereco, Produto, Pedido, ItemPedido
    
    # Importa o 'main' (nosso Blueprint) do arquivo routes.py
    from routes import main as main_blueprint
    
    app.register_blueprint(main_blueprint)


    with app.app_context():
        # db.create_all() # Descomentado por segurança
        print("Contexto da aplicação criado com sucesso.")


    return app

# --- Ponto de Entrada ---
app = create_app()
if __name__ == '__main__':

    app.run(debug=True)
    