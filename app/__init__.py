import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate 

# --- Inicialización de la Aplicación y Configuración ---

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui' 

# --- Inicialización de Extensiones (ANTES de importar modelos) ---

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message_category = 'info'
migrate = Migrate(app, db) 

# --- Importar Modelos y Rutas ---
from . import models 
from . import routes 
from .models import User # Importamos User explícitamente para el user_loader


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
