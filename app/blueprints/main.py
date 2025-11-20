from flask import Blueprint, render_template
from app.models import Book 
from flask import current_app

# Crear el blueprint
bp_main = Blueprint('main', __name__)
# -------------------- RUTAS PÚBLICAS --------------------
@bp_main.route("/")
def index():
    all_books = Book.query.order_by(Book.id.asc()).limit(10).all()

    mas_vendidos = all_books[:5]  
    recomendados = all_books[5:10] 
    
    s3_config = {
        'BASE_URL': f"https://{current_app.config.get('AWS_S3_BUCKET')}.s3.{current_app.config.get('AWS_REGION')}.amazonaws.com/"
    }
    
    return render_template('index.html', 
                           title='Inicio', 
                           mas_vendidos=mas_vendidos,
                           recomendados=recomendados,
                           s3_config=s3_config)

@bp_main.route("/about")
def about():
    return render_template('about.html', title='Acerca de')

@bp_main.route("/soporte")
def soporte():
    return render_template('soporte.html', title='Soporte')
