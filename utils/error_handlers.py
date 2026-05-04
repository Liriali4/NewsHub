"""
NewsHub — Error Handlers e Decoradores
Tratamento centralizado de erros e autenticação
"""

from functools import wraps
from flask import session, jsonify

def require_auth(f):
    """
    Decorator que verifica autenticação do utilizador
    Se não autenticado, retorna 401
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado', 'code': 'UNAUTHORIZED'}), 401
        return f(*args, **kwargs)
    return decorated_function


def api_error(message, code, status):
    """
    Retorna resposta de erro padronizada em JSON
    """
    return jsonify({
        'error': message,
        'code': code
    }), status
