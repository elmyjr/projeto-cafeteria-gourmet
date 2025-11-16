

# 1. Importe o 'db' do nosso novo arquivo 'extensions.py'+
#    (NÃO HÁ MAIS NENHUMA IMPORTAÇÃO DO 'app.py' AQUI)
from extensions import db

# --- Definição dos Modelos (Tabelas) ---

class Cliente(db.Model):
    __tablename__ = 'cliente'
    clienteID = db.Column('clienteid', db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    telefone = db.Column(db.String(15))
    
    # Relacionamentos
    enderecos = db.relationship('Endereco', back_populates='cliente', lazy=True)
    pedidos = db.relationship('Pedido', back_populates='cliente', lazy=True)
class Endereco(db.Model):
    __tablename__ = 'endereco'
    enderecoID = db.Column('enderecoid', db.Integer, primary_key=True)
    clienteID = db.Column('clienteid', db.Integer, db.ForeignKey('cliente.clienteid'), nullable=False)
    rua = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    
    # Relacionamentos
    cliente = db.relationship('Cliente', back_populates='enderecos')
    pedidos = db.relationship('Pedido', back_populates='endereco', lazy=True)

class Produto(db.Model):
    __tablename__ = 'produto'
    produtoID = db.Column('produtoid', db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    tipo = db.Column(db.String(50))
    imagem = db.Column(db.String(100), nullable=True)
    
    # Relacionamentos
    itens_pedido = db.relationship('ItemPedido', back_populates='produto', lazy=True)
class Pedido(db.Model):
    __tablename__ = 'pedido'
    pedidoID = db.Column('pedidoid', db.Integer, primary_key=True)
    clienteID = db.Column('clienteid', db.Integer, db.ForeignKey('cliente.clienteid'), nullable=False)
    enderecoID = db.Column('enderecoid', db.Integer, db.ForeignKey('endereco.enderecoid'), nullable=False)
    data = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    status = db.Column(db.String(50), nullable=False, default='Aguardando Pagamento')
    valorTotal = db.Column('valortotal', db.Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    cliente = db.relationship('Cliente', back_populates='pedidos')
    endereco = db.relationship('Endereco', back_populates='pedidos')
    itens_pedido = db.relationship('ItemPedido', back_populates='pedido', lazy=True)

class ItemPedido(db.Model):
    __tablename__ = 'itempedido'
    itemPedidoID = db.Column('itempedidoid', db.Integer, primary_key=True)
    pedidoID = db.Column('pedidoid', db.Integer, db.ForeignKey('pedido.pedidoid'), nullable=False)
    produtoID = db.Column('produtoid', db.Integer, db.ForeignKey('produto.produtoid'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    precoUnitario = db.Column('precounitario', db.Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    pedido = db.relationship('Pedido', back_populates='itens_pedido')
    produto = db.relationship('Produto', back_populates='itens_pedido')