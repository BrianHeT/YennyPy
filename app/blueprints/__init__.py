from .main import bp_main
from .auth import bp_auth
from .books import bp_books

blueprints = [bp_main, bp_auth, bp_books]

__all__ = ['blueprints']