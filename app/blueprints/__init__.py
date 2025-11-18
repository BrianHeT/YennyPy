from .main import bp_main
from .auth import bp_auth
from .books import bp_books
from .admin import bp_admin

blueprints = [bp_main, bp_auth, bp_books, bp_admin]

__all__ = ['blueprints']