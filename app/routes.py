from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import database, bcrypt   
from .models import User, Book
from .forms import RegistrationForm 

# Crear el blueprint
bp = Blueprint('main', __name__)

# -------------------- RUTAS PÚBLICAS --------------------

@bp.route("/")
@bp.route("/index")
def index():
    return render_template('index.html', title='Inicio')

@bp.route("/about")
def about():
    return render_template('about.html', title='Acerca de')

# -------------------- CATÁLOGO DE LIBROS --------------------
@bp.route("/library")
def library():
    all_books = Book.query.order_by(Book.title.asc()).all()
    return render_template('library.html', title='Biblioteca Completa', books=all_books)

# -------------------- DETALLE DEL LIBRO --------------------
@bp.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', 
                           title=book.title, 
                           book=book)

# -------------------- REGISTRO DE USUARIO --------------------

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password_hash=hashed_password)
        database.session.add(user)
        database.session.commit()
        flash(f'¡Cuenta creada para {form.name.data}! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html', title='Registro', form=form)

# -------------------- INICIO DE SESIÓN --------------------

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user, remember=True) 
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Error de inicio de sesión. Por favor, verifica el email y la contraseña.', 'danger')

    return render_template('login.html', title='Iniciar Sesión') 

# -------------------- CIERRE DE SESIÓN --------------------

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# -------------------- RUTA PERFIL USUARIO --------------------

@bp.route("/profile")
@login_required 
def profile():
    return render_template('profile.html', title='Perfil', user=current_user)