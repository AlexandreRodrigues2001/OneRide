from flask import Flask, flash, render_template, request, url_for, redirect, session
from flask.helpers import flash
from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, EmailField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_
from models import *

app = Flask(__name__)
app.secret_key = 'teste' 
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = 'static/imagens'


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)


#INDEX / INDEX ADMIN / PESQUISAR
@app.route('/')
def index():
    products = Product.query.all()

    return render_template('index.html', products=products)

@app.route('/index_admin')
def index_admin():
    products = Product.query.all()

    return render_template('index_admin.html', products=products)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('index'))

    products = Product.query.filter(Product.nome.ilike(f'%{query}%')).all()

    return render_template('search_results.html', query=query, products=products)

@app.route('/search_admin', methods=['GET'])
def search_admin():
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('index_admin'))

    products = Product.query.filter(Product.nome.ilike(f'%{query}%')).all()

    return render_template('search_results_admin.html', query=query, products=products)
#--------------------
# LOGIN / LOGOUT / ADMIN LOGIN / LOGOUT ADMIN / REGISTER /  REGISTER_ADMIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user is not None and user.check_password(password):
            session['user_id'] = user.user_id
            session['email'] = user.email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin = Admin.query.filter_by(email=email).first()

        if admin is not None and admin.check_password(password):
            session['admin_id'] = admin.admin_id
            print("Admin logged in successfully.")
            return redirect(url_for('index_admin'))
        else:
            return render_template('admin_login.html', error='Invalid email or password')

@app.route('/logout_admin')
def logout_admin():
    session.pop('admin_id', None)
    flash('Logout com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/registry', methods=['GET', 'POST'])
def registry():
    if request.method == 'GET':
        return render_template('registry.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('registry.html', error='E-mail já registrado.')

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.user_id
        session['email'] = new_user.email

        return redirect(url_for('index'))

@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if request.method == 'GET':
        return render_template('add_admin.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('add_admin.html', error='E-mail já registrado.')

        new_user = Admin(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['admin_id'] = new_user.admin_id

        return redirect(url_for('admin_login'))

#--------------------
# PERFIL
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        localidade = request.form['localidade']
        rua = request.form['rua']
        numero_porta = request.form['numero_porta']
        codigo_postal = request.form['codigo_postal']
        numero_cartao = request.form['numero_cartao']
        validade = request.form['validade']
        cvv = request.form['cvv']

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.localidade = localidade
        user.rua = rua
        user.numero_porta = numero_porta
        user.codigo_postal = codigo_postal
        user.numero_cartao = numero_cartao
        user.validade = validade
        user.cvv = cvv

        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        if user:
            allowed_fields = ['name', 'email', 'localidade', 'rua', 'numero_porta', 'codigo_postal', 'numero_cartao', 'validade', 'cvv']

            for field in allowed_fields:
                form_value = request.form.get(field)
                
                if form_value is not None and form_value != '':
                    setattr(user, field, form_value)

            if 'profile_image' in request.files:
                profile_image = request.files['profile_image']
                if profile_image.filename != '' and profile_image.mimetype.startswith('image'):
                    filename = secure_filename(profile_image.filename)
                    profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user.profile_image = filename
                else:
                    flash('Por favor, selecione uma imagem válida.', 'error')

            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Utilizador não encontrado.', 'error')
    else:
        flash('Faça login para atualizar o perfil.', 'warning')

    return redirect(url_for('login'))


#--------------------
# PRODUTOS
@app.route('/products/<int:product_id>', methods=['GET'])
def product_single(product_id):
    product = Product.query.get(product_id)

    if product is None:
        return render_template('404.html'), 404

    return render_template('product_single.html', product=product)

@app.route('/products_admin/<int:product_id>', methods=['GET'])
def product_single_admin(product_id):
    product = Product.query.get(product_id)

    if product is None:
        return render_template('404.html'), 404

    return render_template('product_single_admin.html', product=product)

class AddProductForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    especificacoes = TextAreaField('Especificações', validators=[DataRequired()])
    foto = FileField('Foto', validators=[DataRequired(), FileAllowed(['jpg', 'png'], 'Apenas imagens .jpg e .png são permitidas.')])

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()

    if form.validate_on_submit():
        nome = form.nome.data
        valor = form.valor.data
        descricao = form.descricao.data
        especificacoes = form.especificacoes.data

        # Substituir quebras de linha
        descricao = descricao.replace('\n', '<br>')
        especificacoes = especificacoes.replace('\n', '<br>')

        if form.foto.data:
            try:
                photo = form.foto.data
                filename = secure_filename(photo.filename)
                photo_path = f'static/imagens/{filename}'
                photo.save(photo_path)

                new_product = Product(nome=nome, valor=valor, descricao=descricao, especificacoes=especificacoes, photo=filename)
                db.session.add(new_product)
                db.session.commit()

                flash('Produto adicionado com sucesso!', 'success')
                return redirect(url_for('index_admin'))
            except Exception as e:
                print(f"Erro ao adicionar produto")
                flash('Ocorreu um erro ao adicionar o produto. Tente novamente.', 'error')

    return render_template('add_product.html', form=form)

@app.route('/delete_product_admin/<int:product_id>', methods=['POST'])
def delete_product_admin(product_id):
    product = Product.query.get(product_id)

    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Produto removido com sucesso.', 'success')
    else:
        flash('Produto não encontrado.', 'error')

    return redirect(url_for('index_admin'))

@app.route('/edit_product_admin/<int:product_id>', methods=['GET', 'POST'])
def edit_product_admin(product_id):
    app.logger.debug(f'Editando o produto com ID {product_id}')
    product = Product.query.get(product_id)

    if product is None:
        return render_template('404.html'), 404

    if request.method == 'POST':
        allowed_fields = ['nome', 'valor', 'descricao', 'especificacoes']
        for field in allowed_fields:
            form_value = request.form.get(field)
            if form_value is not None:
                if field in ['descricao', 'especificacoes']:
                    form_value = form_value.replace('\n', '<br>')
                setattr(product, field, form_value)


        if 'Foto' in request.files:
            if 'Foto' in request.files:
                app.logger.debug('Campo "Foto" encontrado nos arquivos da solicitação.')
                photo = request.files['Foto']
                if photo.filename != '' and photo.mimetype.startswith('image'):
                    filename = secure_filename(photo.filename)
                    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    photo.save(photo_path)
                    product.photo = filename
                else:
                    app.logger.debug('Campo "Foto" NÃO encontrado nos arquivos da solicitação.')
                    flash('Por favor, selecione uma imagem.', 'error')

        db.session.commit()
        app.logger.debug('Alterações confirmadas no banco de dados')
        flash('Alterações salvas com sucesso!', 'success')
        return redirect(url_for('index_admin'))

    return render_template('product_single_admin.html', product=product)
#--------------------
# CARRINHO
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)

            cart = user.cart

            if cart:
                cart_items = cart.items
                total_price = sum(item.product.valor * item.quantity for item in cart_items)
            else:
                cart_items = []
                total_price = 0

            products = [item.product for item in cart_items]

            return render_template('cart.html', cart=cart, products=products, total_price=total_price)
        else:
            return redirect(url_for('login'))

    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)

            product_id = request.form['prod_id']
            product = Product.query.get(product_id)
            quantity = int(request.form['quantity'])

            cart = user.cart

            existing_item = CartItem.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()

            if existing_item:
                flash(f'{product.nome} já foi adicionado ao carrinho.', 'warning')
            else:
                cart_item = CartItem(cart=cart, product=product, quantity=quantity)
                db.session.add(cart_item)
                db.session.commit()
                flash(f'{product.nome} adicionado ao carrinho com sucesso!', 'success')

            return redirect(url_for('cart'))
        else:
            return redirect(url_for('login'))

@app.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    product = Product.query.get(product_id)

    if not product:
        return render_template('404.html'), 404

    if not user.cart:
        user_cart = Cart(user_id=user_id)
        db.session.add(user_cart)
    else:
        user_cart = user.cart

    existing_cart_item = CartItem.query.filter_by(cart_id=user_cart.cart_id, product_id=product_id).first()

    if existing_cart_item:
        flash(f'{product.nome} já está no seu carrinho.', 'info')
    else:
        cart_item = CartItem(cart_id=user_cart.cart_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
        flash(f'{product.nome} adicionado ao carrinho com sucesso!', 'success')

    db.session.commit()

    return redirect(url_for('cart'))

@app.route('/update_cart_item/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    cart_item = CartItem.query.get(item_id)

    if not cart_item:
        flash('Item do carrinho não encontrado.', 'error')
        return redirect(url_for('cart'))

    if cart_item.cart.user_id != user_id:
        flash('Você não tem permissão para atualizar este item do carrinho.', 'error')
        return redirect(url_for('cart'))

    if request.form['action'] == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
            flash(f'Quantidade de {cart_item.product.nome} diminuída com sucesso.', 'success')
    elif request.form['action'] == 'increase':
        cart_item.quantity += 1
        db.session.commit()
        flash(f'Quantidade de {cart_item.product.nome} aumentada com sucesso.', 'success')

    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    cart_item = CartItem.query.get(item_id)

    if not cart_item:
        flash('Item do carrinho não encontrado.', 'error')
    elif cart_item.cart.user_id != user_id:
        flash('Você não tem permissão para remover este item do carrinho.', 'error')
    else:
        db.session.delete(cart_item)
        db.session.commit()
        flash(f'{cart_item.product.nome} removido do carrinho com sucesso.', 'success')

    return redirect(url_for('cart'))
#--------------------
#CHECKOUT
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)

            cart = user.cart

            if cart:
                cart_items = cart.items
                total_price = sum(item.product.valor * item.quantity for item in cart_items)
            else:
                cart_items = []
                total_price = 0

            products = [item.product for item in cart_items]

            return render_template('checkout.html', user=user, cart=cart, products=products, total_price=total_price)
        else:
            return redirect(url_for('login'))

        
@app.route('/update_checkout_item/<int:item_id>', methods=['POST'])
def update_checkout_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    cart_item = CartItem.query.get(item_id)

    if not cart_item:
        flash('Item do checkout não encontrado.', 'error')
        return redirect(url_for('checkout'))

    if cart_item.cart.user_id != user_id:
        flash('Você não tem permissão para atualizar este item do checkout.', 'error')
        return redirect(url_for('checkout'))

    if request.form['action'] == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
            flash(f'Quantidade de {cart_item.product.nome} diminuída com sucesso.', 'success')
    elif request.form['action'] == 'increase':
        cart_item.quantity += 1
        db.session.commit()
        flash(f'Quantidade de {cart_item.product.nome} aumentada com sucesso.', 'success')

    return redirect(url_for('checkout'))

@app.route('/remove_from_checkout/<int:item_id>', methods=['POST'])
def remove_from_checkout(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    cart_item = CartItem.query.get(item_id)

    if not cart_item:
        flash('Item do carrinho não encontrado.', 'error')
    elif cart_item.cart.user_id != user_id:
        flash('Você não tem permissão para remover este item do carrinho.', 'error')
    else:
        db.session.delete(cart_item)
        db.session.commit()
        flash(f'{cart_item.product.nome} removido do carrinho com sucesso.', 'success')

    return redirect(url_for('checkout'))

#TICKETS
class AddTicketForm(FlaskForm):
    email = StringField('Email')
    assunto = StringField('Assunto', validators=[DataRequired()])
    descricao = StringField('Descricao', validators=[DataRequired()])
    foto = FileField('Foto')

@app.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    form = AddTicketForm()

    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        

        if user:
            if request.method == 'GET':
                form.email.data = user.email

            if form.validate_on_submit():
                email_user = form.email.data
                assunto = form.assunto.data
                descricao = form.descricao.data
                foto = form.foto.data

                if foto:
                    filename = secure_filename(foto.filename)
                    foto_path = f'static/imagens/{filename}'
                    foto.save(foto_path)
                else:
                    filename = 'default.jpg'

                descricao = descricao.replace('\n', '<br>')
                new_ticket = Ticket(email_user=email_user, assunto=assunto, descricao=descricao, foto=filename, tratado=False)
                db.session.add(new_ticket)
                db.session.commit()

                flash('Ticket adicionado com sucesso!', 'success')
                return redirect(url_for('index'))

            return render_template('add_ticket.html', form=form)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    
@app.route('/tickets', methods=['GET'])
def list_tickets():
    query = request.args.get('query')
    order_by = request.args.get('order_by', 'asc') 
    if order_by == 'asc':
        order_clause = Ticket.data_hora.asc()
    elif order_by == 'desc':
        order_clause = Ticket.data_hora.desc()
    else:
        order_clause = Ticket.data_hora.asc()

    if query:
        tickets = Ticket.query.filter(Ticket.tratado == False,or_(Ticket.email_user.ilike(f'%{query}%'))).order_by(order_clause).all()
    else:
        tickets = Ticket.query.filter_by(tratado=False).order_by(order_clause).all()

    return render_template('list_tickets.html', tickets=tickets)
@app.route('/tickets_history', methods=['GET'])
def list_tickets_history():
    query = request.args.get('query')
    order_by = request.args.get('order_by', 'asc') 
    if order_by == 'asc':
        order_clause = Ticket.data_hora.asc()
    elif order_by == 'desc':
        order_clause = Ticket.data_hora.desc()
    else:
        order_clause = Ticket.data_hora.asc()

    if query:
        tickets = Ticket.query.filter(Ticket.tratado == True,or_(Ticket.email_user.ilike(f'%{query}%'))).order_by(order_clause).all()
    else:
        tickets = Ticket.query.filter_by(tratado=True).order_by(order_clause).all()

    return render_template('historico_tickets.html', tickets=tickets)

@app.route('/ticket/<int:ticket_id>', methods=['GET'])
def ticket_single(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket_single.html', ticket=ticket)

@app.route('/resolve_ticket/<int:ticket_id>', methods=['POST'])
def resolve_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.tratado = True 
    db.session.commit()

    flash('Ticket resolvido com sucesso!', 'success')
    return redirect(url_for('index_admin'))

@app.route('/unresolve_ticket/<int:ticket_id>', methods=['POST'])
def unresolve_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.tratado = False
    db.session.commit()

    flash('Ticket resolvido com sucesso!', 'success')
    return redirect(url_for('index_admin'))
#--------------------
#ERRO 404   
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
#--------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)