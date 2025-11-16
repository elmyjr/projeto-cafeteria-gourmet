# routes.py
# Aqui ficam todas as rotas da aplicação.

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import Cliente, Produto, Pedido, ItemPedido, Endereco

# "Blueprint"

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Rota principal (Homepage)
    """
    try:
        produtos_do_banco = Produto.query.all()
        return render_template('home.html', produtos=produtos_do_banco)
    except Exception as e:
        return f'ERRO AO RENDERIZAR O TEMPLATE: <br>{e}'
    

# ROTA PRODUTO
@main.route('/produto/<int:produto_id>')
def produto(produto_id):
    """
    Rota para exibir a página de detalhes de um produto específico.
    """
    # 1. Busca o produto no banco pelo ID, ou retorna um erro 404 se não achar.
    produto = Produto.query.get_or_404(produto_id)

    # 2. Renderiza o novo template, passando o produto encontrado.
    return render_template('produto.html', produto=produto)
#  FIM DA NOVA ROTA PRODUTO


#  ROTA ADICIONAR AO CARRINHO
@main.route('/adicionar-ao-carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    # Pega os dados do formulário da página de produto
    produto_id = request.form.get('produto_id')
    quantidade = request.form.get('quantidade', 1, type=int) # Pega 1 como padrão

    # Pega a ação (se foi "add_to_cart" ou "buy_now")
    action = request.form.get('action')

    if not produto_id:
        flash("Erro: ID do produto não encontrado.", "error")
        return redirect(request.referrer or url_for('main.index'))

    # 1. Inicializa o carrinho na sessão se for a primeira vez
    if 'carrinho' not in session:
        session['carrinho'] = {}

    # Converte o ID para string 
    produto_id_str = str(produto_id)

    # 2. Adiciona o item ao carrinho
    if produto_id_str in session['carrinho']:
        # Se o item já está lá, apenas soma a quantidade
        session['carrinho'][produto_id_str] += quantidade
    else:
        # Se é um item novo, define a quantidade
        session['carrinho'][produto_id_str] = quantidade

    # 3. Marca a sessão como "modificada" para garantir que salve
    session.modified = True

    flash(f'Produto adicionado a Cesta!', 'success')

    # 4. Redireciona o usuário
    if action == "buy_now":
        # Se clicou em "Finalizar Compra", vai direto para o carrinho
        return redirect(url_for('main.carrinho'))
    else:
        # Se clicou em "Adicionar", volta para a página de onde veio
        return redirect(request.referrer or url_for('main.index'))
    
# FIM DA ROTA ADICIONAR AO CARRINHO
# ROTA CARRINHO DE COMPRAS

@main.route('/carrinho')
def carrinho():
    # Pega o carrinho da sessão (ou um dict vazio se não existir)
    carrinho_session = session.get('carrinho', {})
    
    produtos_no_carrinho = []
    total_carrinho = 0
    
    # Busca os detalhes de cada produto no banco
    for produto_id_str, quantidade in carrinho_session.items():
        produto = Produto.query.get(produto_id_str)
        
        if produto:
            subtotal = produto.preco * quantidade
            produtos_no_carrinho.append({
                "produto": produto,
                "quantidade": quantidade,
                "subtotal": subtotal
            })
            total_carrinho += subtotal
            
    return render_template('carrinho.html', 
                            produtos_no_carrinho=produtos_no_carrinho, 
                            total_carrinho=total_carrinho)
# FIM DA ROTA CARRINHO DE COMPRAS

# ROTA CADASTRO

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # 1. PEGAR OS DADOS DO FORMULÁRIO
        nome = request.form.get('nome')
        email = request.form.get('email')
        cpf_bruto = request.form.get('cpf')
        senha = request.form.get('senha')
        telefone_bruto = request.form.get('telefone') 

        # Limpa o CPF
        if cpf_bruto:
            cpf = "".join(filter(str.isdigit, cpf_bruto))
        else:
            cpf = None

        # Limpa o telefone
        if telefone_bruto:
            telefone = "".join(filter(str.isdigit, telefone_bruto))
        else:
            telefone = None

        if not nome or not email or not cpf or not senha:
            flash("Erro: Todos os campos (exceto telefone) são obrigatórios.", "error")
            return redirect(url_for('main.cadastro'))
        
        # Verifica se o email ou cpf já existem
        if Cliente.query.filter_by(email=email).first():
            flash("Este email já está em uso.", "error")
            return redirect(url_for('main.cadastro'))
        
        if Cliente.query.filter_by(cpf=cpf).first():
            flash("Este CPF já está em uso.", "error")
            return redirect(url_for('main.cadastro'))

        senha_hash = generate_password_hash(senha)

        # 2. CRIAR O NOVO CLIENTE (Model)
        novo_cliente = Cliente(
            nome=nome,
            email=email,
            cpf=cpf,
            senha=senha_hash,
            telefone=telefone
        )
        
        # 3. SALVAR NO BANCO DE DADOS
        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash("Conta criada com sucesso! Faça o login.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao cadastrar: {str(e)}", "error")
            return redirect(url_for('main.cadastro'))

        return redirect(url_for('main.login')) # Manda para o login após cadastrar

    return render_template('cadastro.html')

# FIM DA ROTA CADASTRO

# ROTA LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'cliente_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        next_page = request.form.get('next')

        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'error')
            return redirect(url_for('main.login'))

        # 1. BUSCAR O CLIENTE NO BANCO
        cliente = Cliente.query.filter_by(email=email).first()

        # 2. VERIFICAR SE O CLIENTE EXISTE E A SENHA ESTÁ CORRETA
        if cliente and check_password_hash(cliente.senha, senha):
            
            # 3. REGISTRAR O USUÁRIO NA SESSÃO
            session['cliente_id'] = cliente.clienteID
            session['cliente_nome'] = cliente.nome
            flash('Login efetuado com sucesso!', 'success')
            if next_page and next_page == url_for('main.finalizar_pedido'):
                return redirect(url_for('main.carrinho'))                
            elif next_page:
                return redirect(next_page)                
            else:
                # Se não houver 'next', vá para a Home.
                return redirect(url_for('main.index'))
    next_page_from_url = request.args.get('next')
    return render_template('login.html', next=next_page_from_url)

# FIM DA ROTA LOGIN
# ROTA LOGOUT
@main.route('/logout')
def logout():
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('main.login'))
# FIM DA ROTA LOGOUT

# ROTA NOSSA HISTÓRIA
@main.route('/nossa-historia')
def nossa_historia():
    return render_template('historia.html')
# FIM DA ROTA NOSSA HISTÓRIA

# ROTA ASSINATURAS
@main.route('/assinaturas')
def assinaturas():
    flash("Em breve...", "info")
    # Redireciona o usuário de volta para a página inicial
    return redirect(url_for('main.index'))
# FIM DA ROTA ASSINATURAS

# ROTA ENDEREÇO
@main.route('/adicionar-endereco', methods=['GET', 'POST'])
def adicionar_endereco():
    # Rota de proteção: só para usuários logados
    if 'cliente_id' not in session:
        flash("Você precisa estar logado para acessar esta página.", "error")
        return redirect(url_for('main.login', next=request.path))
    
    if request.method == 'POST':
        # Pega dados do formulário
        rua = request.form.get('rua')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = "".join(filter(str.isdigit, request.form.get('cep')))

        # Pega o ID do cliente da sessão
        cliente_id = session['cliente_id']
        
        # (Simplificação de MVP: apenas cria um novo. 
        #  Uma versão melhor verificaria se já existe e atualizaria)
        
        novo_endereco = Endereco(
            clienteID=cliente_id,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado.upper(),
            cep=cep
        )
        
        try:
            db.session.add(novo_endereco)
            db.session.commit()
            flash("Endereço salvo com sucesso!", "success")
            # Envia o usuário de volta para o carrinho
            return redirect(url_for('main.carrinho')) 
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar endereço: {str(e)}", "error")

    return render_template('endereco.html')
# FIM DA ROTA ENDEREÇO

# ROTA FINALIZAR PEDIDO
@main.route('/finalizar-pedido', methods=['POST'])
def finalizar_pedido():
    # --- 1. VERIFICAÇÕES ---
    
    #  O usuário está logado?
    if 'cliente_id' not in session:
        flash("Você precisa estar logado para finalizar a compra.", "error")
        return redirect(url_for('main.login', next=request.path))
    
    cliente_id = session['cliente_id']
    
    #  O carrinho está vazio?
    carrinho_session = session.get('carrinho', {})
    if not carrinho_session:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for('main.carrinho'))

    #  O usuário tem endereço cadastrado? 
    endereco = Endereco.query.filter_by(clienteID=cliente_id).first()
    if not endereco:
        flash("Você precisa adicionar um endereço antes de finalizar o pedido.", "error")
        # Manda o usuário para a página de adicionar endereço
        return redirect(url_for('main.adicionar_endereco'))

    # Transação
    
    try:
        total_pedido = 0
        itens_para_salvar = []
        
        # Calcula o total
        for produto_id_str, quantidade in carrinho_session.items():
            produto = Produto.query.get(produto_id_str)
            if produto:
                subtotal = produto.preco * quantidade
                total_pedido += subtotal
                itens_para_salvar.append({
                    "produto_obj": produto,
                    "quantidade": quantidade,
                    "preco_unitario": produto.preco
                })

        # Cria o Pedido (Cabeçalho)
        novo_pedido = Pedido(
            clienteID=cliente_id,
            enderecoID=endereco.enderecoID,
            valorTotal=total_pedido,
            status="Processando" 
        )
        db.session.add(novo_pedido)
        
        db.session.flush()

        # Cria os Itens do Pedido (Corpo)
        for item in itens_para_salvar:
            novo_item_pedido = ItemPedido(
                pedidoID=novo_pedido.pedidoID,
                produtoID=item["produto_obj"].produtoID,
                quantidade=item["quantidade"],
                precoUnitario=item["preco_unitario"]
            )
            db.session.add(novo_item_pedido)

        # FINALIZAÇÃO 
        
        # Limpa o carrinho da sessão
        session.pop('carrinho', None)
        session.modified = True
        
        # Salva tudo no banco de dados
        db.session.commit()
        
        flash("Pedido efetuado com sucesso!", "success")
        # Redireciona para a nova página de "Meus Pedidos"
        return redirect(url_for('main.meus_pedidos'))

    except Exception as e:
        db.session.rollback() # Desfaz tudo se der erro
        flash(f"Erro ao finalizar o pedido: {str(e)}", "error")
        return redirect(url_for('main.carrinho'))
# FIM DA ROTA FINALIZAR PEDIDO

# ROTA MEUS PEDIDOS
@main.route('/meus-pedidos')
def meus_pedidos():
    # Rota de proteção
    if 'cliente_id' not in session:
        flash("Você precisa estar logado para ver seus pedidos.", "error")
        return redirect(url_for('main.login' , next=request.path))

    cliente_id = session['cliente_id']
    
    # Busca os pedidos do cliente, do mais novo para o mais antigo
    pedidos_do_cliente = Pedido.query.filter_by(clienteID=cliente_id)\
                                    .order_by(Pedido.data.desc())\
                                    .all()
    
    return render_template('meus_pedidos.html', pedidos=pedidos_do_cliente)
# FIM DA ROTA MEUS PEDIDOS