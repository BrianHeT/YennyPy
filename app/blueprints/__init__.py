from .main import bp_main
from .auth import bp_auth
from .books import bp_books
from .admin import bp_admin
from .carrito import bp_carrito

blueprints = [bp_main, bp_auth, bp_books, bp_admin, bp_carrito]

__all__ = ['blueprints']