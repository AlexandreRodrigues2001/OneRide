from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

from sqlalchemy import CheckConstraint

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64))
    localidade = db.Column(db.String(128))
    rua = db.Column(db.String(128))
    numero_porta = db.Column(db.String(16))
    codigo_postal = db.Column(db.String(8))
    numero_cartao = db.Column(db.String(16))
    validade = db.Column(db.String(5))
    cvv = db.Column(db.String(3))
    profile_image = db.Column(db.String(128), nullable=True, default='static/imagens/user.jpg')


    def __init__(self, email, password, name=None, localidade=None, rua=None, numero_porta=None, codigo_postal=None, numero_cartao=None, validade=None, cvv=None, profile_image='default.jpg'):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.localidade = localidade
        self.rua = rua
        self.numero_porta = numero_porta
        self.codigo_postal = codigo_postal
        self.numero_cartao = numero_cartao
        self.validade = validade
        self.cvv = cvv
        self.profile_image = profile_image

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
    
    def profile_complete(self):
        return all(
            getattr(self, field) is not None
            for field in ['name', 'email', 'localidade', 'rua', 'numero_porta', 'codigo_postal', 'numero_cartao', 'validade', 'cvv']
        )
    
    cart = db.relationship('Cart', backref='user', uselist=False)


#db Admin
class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        print (check_password_hash(self.password_hash, password))
        return check_password_hash(self.password_hash, password)

#db Product
class Product(db.Model):
    __tablename__ = 'products'
    prod_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text)
    especificacoes = db.Column(db.Text)
    photo = db.Column(db.String(128), nullable=False)

    def __init__(self, nome, valor, descricao=None, especificacoes=None, photo=None):
        self.nome = nome
        self.valor = valor
        self.descricao = descricao
        self.especificacoes = especificacoes
        self.photo = photo

    def __repr__(self):
        return f'<Product {self.nome}>'

#db Cart e CartItem
class Cart(db.Model):
    __tablename__ = 'carts'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    items = db.relationship('CartItem', backref='cart')

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.cart_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.prod_id'))
    quantity = db.Column(db.Integer)

    product = db.relationship('Product', lazy='subquery', uselist=False)

#db tickets
class Ticket(db.Model):
    id_ticket = db.Column(db.Integer, primary_key=True)
    email_user = db.Column(db.String(120), nullable=False)
    assunto = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    data_hora = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    foto = db.Column(db.String(255))
    tratado = db.Column(db.Boolean, default=False, nullable=False)
