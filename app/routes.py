
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt 
from app.forms import RegistrationForm 
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

# -------------------- RUTAS PÚBLICAS --------------------

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', title='Inicio')

@app.route("/about")
def about():
    return render_template('about.html', title='Acerca de')

@app.route("/signinautor")
def signinautor():
    return render_template('signinautor.html', title='perfil Autor')


# -------------------- REGISTRO DE USUARIO --------------------

@app.route("/register", methods=['GET', 'POST'])
def register():
    # Si el usuario ya está logueado, redirige a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Hashear la contraseña usando Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Crear una nueva instancia de usuario
        user = User(name=form.name.data, email=form.email.data, password_hash=hashed_password)
        
        # Guardar el usuario en la base de datos
        db.session.add(user)
        db.session.commit()
        
        # Mensaje de éxito
        flash(f'¡Cuenta creada para {form.name.data}! Ahora puedes iniciar sesión.', 'success')
        
        # Redirigir al login
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Registro', form=form)

# -------------------- INICIO DE SESIÓN --------------------

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Buscar el usuario por email
        user = User.query.filter_by(email=request.form.get('email')).first()
        
        #Verificar si el usuario existe y si la contraseña es correcta
        if user and bcrypt.check_password_hash(user.password_hash, request.form.get('password')):
            # Iniciar sesión con Flask-Login
            login_user(user, remember=True) 
            
            # Redirigir a la página a la que quería acceder (si existe) o al index
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Error de inicio de sesión. Por favor, verifica el email y la contraseña.', 'danger')

    # Usar tu plantilla de login/register (signin.html o similar)
    return render_template('login.html', title='Iniciar Sesión') 

# -------------------- CIERRE DE SESIÓN --------------------

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

# -------------------- RUTA PERFIL USUARIO --------------------

@app.route("/profile")
@login_required 
def profile():
    return render_template('profile.html', title='Perfil', user=current_user)