from flask import Blueprint
from flask_login import LoginManager, login_required
from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.exceptions import HTTPException 


bp_error = Blueprint("errors", __name__)

# -------------------- MANEJADORES DE ERRORES --------------------

@bp_error.app_errorhandler(404)
def error_404(error):
    # Retorna la plantilla 404 con el código de estado 404
    return render_template('errors/404.html', title='404'), 404

@bp_error.app_errorhandler(403)
def error_403(error):
    # Prohibido (útil para errores de permisos de admin)
    return render_template('errors/403.html', title='403'), 403

@bp_error.app_errorhandler(500)
def error_500(error):
    # Error interno del servidor
    return render_template('errors/500.html', title='500'), 500

# -------------------- TRATAMIENTO ESPECIAL PARA LOGIN --------------------

@bp_error.app_errorhandler(401)
def error_401(error):
    flash("Por favor, inicia sesión para acceder a esta página.", "warning")
    return redirect(url_for('main.index'))

@bp_error.route("/cart")
@login_required
def cart():
    # Aquí va la lógica para mostrar el carrito
    return render_template('cart.html', title='Carrito')
