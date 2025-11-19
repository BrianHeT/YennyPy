from flask import Blueprint, render_template

# Crear el blueprint
bp_main = Blueprint('main', __name__)
# -------------------- RUTAS PÚBLICAS --------------------
@bp_main.route("/")
def index():
    return render_template('index.html', title='Inicio')

@bp_main.route("/about")
def about():
    return render_template('about.html', title='Acerca de')

#@bp_main.route("/soporte")
#def soporte():
 #   return render_template('soporte.html', title='Soporte')
