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


# import os
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from dotenv import load_dotenv

# # 1. Importe o 'db' do nosso novo arquivo 'extensions.py'
# from extensions import db

# def create_app():
#     """
#     Usa o padrão Factory para criar a aplicação Flask.
#     """
#     app = Flask(__name__)
#     load_dotenv() # Carrega as variáveis do .env

#     # --- Configuração do Banco de Dados ---
#     db_url = os.getenv('DATABASE_URL')

#     if not db_url:
#         raise ValueError("ERRO: DATABASE_URL não foi encontrada no arquivo .env")

#     # Corrige 'postgres://' para 'postgresql://' (exigência do SQLAlchemy)
#     if db_url.startswith("postgres://"):
#         db_url = db_url.replace("postgres://", "postgresql://", 1)

#     app.config['SQLALCHEMY_DATABASE_URI'] = db_url
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

#     # 2. Conecta a instância 'db' (de extensions.py) com o app Flask
#     #    Isto "registra" o db.
#     db.init_app(app)
#     # --- Importação de Modelos e Rotas ---
#     # Importamos os modelos AQUI, dentro do contexto,
#     # para garantir que o 'db' já esteja configurado.
    
#     # Esta importação agora é 100% segura.
#     # Precisamos importar todos eles aqui para que o SQLAlchemy
#     # saiba sobre todas as suas tabelas.
#     from models import Cliente, Endereco, Produto, Pedido, ItemPedido

#     with app.app_context():
#         # db.create_all() # Descomentado por segurança
#         print("Contexto da aplicação criado com sucesso.")


    # # --- Rotas (Controlador) ---
    # @app.route('/')
    # def index():
    #     """
    #     Rota principal (homepage).
    #     """
    #     produtos_do_banco = Produto.query.all()
    #     try:
    #         produtos_do_banco = Produto.query.all()
    #         return render_template('home.html', produtos=produtos_do_banco)
    #     except Exception as e:
    #         # Retorna o erro específico se a consulta falhar
    #         return f'ERRO AO RENDERIZAR O TEMPLATE: <br>{e}'
    # # Rota de Cadastro de Cliente
    # @app.route('/cadastro', methods=['GET', 'POST'])
    # def cadastro():
        
    #     # Se o usuário está ENVIANDO o formulário (POST)
    #     if request.method == 'POST':
    #         # 1. PEGAR OS DADOS DO FORMULÁRIO
    #         nome = request.form.get('nome')
    #         email = request.form.get('email')
    #         telefone = request.form.get('telefone')
    #         cpf = request.form.get('cpf')
    #         senha = request.form.get('senha')
    #         if cpf:
    #             cpf = "".join(filter(str.isdigit, cpf))
    #         else:
    #             cpf = None
    #         if telefone:
    #             telefone = "".join(filter(str.isdigit, telefone))
    #         else:
    #             telefone = None
            
    #         # (Validação simples - você pode melhorar depois)
    #         if not nome or not email or not cpf or not senha:
    #             # (No futuro, é melhor enviar uma mensagem de erro)
    #             return "Erro: Todos os campos são obrigatórios."
            
    #         #  HASHING DA SENHA
    #         senha_hash = generate_password_hash(senha)

    #         # 2. CRIAR O NOVO CLIENTE (Model)
    #         # (Certifique-se que 'Cliente' está importado de 'models' no topo da função)
    #         novo_cliente = Cliente(
    #             nome=nome,
    #             email=email,
    #             telefone=telefone,
    #             cpf=cpf,
    #             senha=senha_hash 
    #             # O 'telefone' é opcional, então não precisamos dele aqui
    #         )
            
    #         # 3. SALVAR NO BANCO DE DADOS
    #         try:
    #             db.session.add(novo_cliente) # Adiciona
    #             db.session.commit()          # Salva (Faz o "commit")
    #         except Exception as e:
    #             db.session.rollback() # Desfaz em caso de erro
    #             return f"Erro ao cadastrar: {str(e)}"

    #         # 4. REDIRECIONAR para a página de login (ou home)
    #         # (Vamos criar a rota /login em breve)
    #         return redirect(url_for('index')) # Por enquanto, volta para a home


    #     # Se o usuário está APENAS ACESSANDO a página (GET)
    #     # Apenas mostre o HTML do formulário
    #     return render_template('cadastro.html')

    # # ... (rota de cadastro) ...


    # # ROTA DE LOGIN 
    # @app.route('/login', methods=['GET', 'POST'])
    # def login():
    #     # Se o usuário já está logado, manda ele para a home
    #     if 'cliente_id' in session:
    #         flash('Usuário logado', 'Usuário logado')
    #         return redirect(url_for('index'))

    #     if request.method == 'POST':
    #         email = request.form.get('email')
    #         senha = request.form.get('senha')

    #         if not email or not senha:
    #             flash('Email e senha são obrigatórios.', 'error')
    #             return redirect(url_for('login'))

    #         # 1. BUSCAR O CLIENTE NO BANCO
    #         # (Certifique-se que 'Cliente' está importado de 'models')
    #         cliente = Cliente.query.filter_by(email=email).first()

    #         # 2. VERIFICAR SE O CLIENTE EXISTE E A SENHA ESTÁ CORRETA
    #         # check_password_hash compara a senha do formulário com o hash do banco
    #         if cliente and check_password_hash(cliente.senha, senha):
                
    #             # 3. REGISTRAR O USUÁRIO NA SESSÃO
    #             # "Lembramos" dele salvando seu ID
    #             session['cliente_id'] = cliente.clienteID
    #             session['cliente_nome'] = cliente.nome
    #             flash('Login efetuado com sucesso!', 'success')
    #             return redirect(url_for('index'))
    #         else:
    #             # Se o cliente não existe ou a senha está errada
    #             flash('Email ou senha inválidos.', 'error')
    #             return redirect(url_for('login'))

    #     # Se for GET, apenas mostra a página de login
    #     return render_template('login.html')

    
    # #  ROTA DE LOGOUT 
    # @app.route('/logout')
    # def logout():
    #     # Remove os dados do cliente da sessão
    #     session.pop('cliente_id', None)
    #     session.pop('cliente_nome', None)
    #     flash('Você saiu da sua conta.', 'success')
    #     return redirect(url_for('login'))
    # # ...
    # return app
    # # Registre outras rotas aqui no futuro...

#     return app
# # --- Ponto de Entrada ---
# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True)