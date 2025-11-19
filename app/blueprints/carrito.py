from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import database
from app.models import Book, CartItem
from sqlalchemy.orm import joinedload

bp_carrito = Blueprint("carrito", __name__, url_prefix="/carrito")

# -------------------- VISTA DEL CARRITO --------------------

@bp_carrito.route("/")
@login_required
def cart():
    cart_items = database.session.query(CartItem).options(
        joinedload(CartItem.book)
    ).filter(CartItem.user_id == current_user.id).all()
    
    total_price = sum(item.cantidad * item.book.price for item in cart_items)
    
    s3_config = {
        'BASE_URL': f"https://{current_app.config.get('AWS_S3_BUCKET')}.s3.{current_app.config.get('AWS_REGION')}.amazonaws.com/"
    }
    
    return render_template('carrito_user.html',  
                           title='Mi Carrito', 
                           cart_items=cart_items, 
                           total_price=total_price,
                           s3_config=s3_config) 

# -------------------- AÑADIR AL CARRITO --------------------

@bp_carrito.route("/agregar/<int:book_id>", methods=['POST'])
@login_required
def cart_add_item(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Validar stock disponible
    if book.quantity <= 0:
        flash(f'"{book.title}" no está disponible en stock.', 'warning')
        return redirect(request.referrer or url_for('books.list_books'))
    
    item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    
    if item:
        # Validar que no exceda el stock
        if item.cantidad >= book.quantity:
            flash(f'Ya tienes el máximo disponible de "{book.title}" en tu carrito.', 'warning')
        else:
            item.cantidad += 1
            database.session.commit()
            flash(f'Cantidad de "{book.title}" actualizada en el carrito.', 'info')
    else:
        new_item = CartItem(user_id=current_user.id, book_id=book_id, cantidad=1)
        database.session.add(new_item)
        database.session.commit()
        flash(f'"{book.title}" añadido al carrito.', 'success')
    
    return redirect(request.referrer or url_for('carrito.cart'))

# -------------------- ACTUALIZAR CANTIDAD --------------------

@bp_carrito.route("/actualizar/<int:item_id>", methods=['POST'])
@login_required
def cart_update(item_id):
    item = CartItem.query.get_or_404(item_id)
    
    if item.user_id != current_user.id:
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('carrito.cart'))

    try:
        new_cantidad = int(request.form.get('cantidad', 0))
        
        if new_cantidad <= 0:
            flash('La cantidad debe ser mayor que cero.', 'warning')
        elif new_cantidad > item.book.quantity:
            flash(f'Solo hay {item.book.quantity} unidades disponibles de "{item.book.title}".', 'warning')
        else:
            item.cantidad = new_cantidad
            database.session.commit()
            flash('Cantidad actualizada con éxito.', 'success')

    except (ValueError, TypeError):
        flash('Cantidad inválida.', 'danger')

    return redirect(url_for('carrito.cart'))

# -------------------- ELIMINAR DEL CARRITO --------------------

@bp_carrito.route("/eliminar/<int:item_id>", methods=['POST'])
@login_required
def cart_remove_item(item_id):
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        flash('Acción no autorizada.', 'danger')
        return redirect(url_for('carrito.cart'))

    book_title = item.book.title
    database.session.delete(item)
    database.session.commit()
    flash(f'"{book_title}" eliminado del carrito.', 'info')
    return redirect(url_for('carrito.cart'))

# -------------------- VACIAR CARRITO --------------------

@bp_carrito.route("/vaciar", methods=['POST'])
@login_required
def cart_clear():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    database.session.commit()
    flash('Carrito vaciado.', 'info')
    return redirect(url_for('carrito.cart'))