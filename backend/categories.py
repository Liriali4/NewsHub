"""
NewsHub — Blueprint de Preferências
GET /api/preferences, PUT /api/preferences
"""

from flask import Blueprint, request, session, jsonify
from utils.error_handlers import require_auth, api_error

categories_bp = Blueprint('categories', __name__, url_prefix='/api')

VALID_CATEGORIES = [
    'tecnologia', 'desporto', 'saude', 'ciencia', 'negocios', 'entretenimento'
]


@categories_bp.route('/preferences', methods=['GET'])
@require_auth
def get_preferences():
    """
    GET /api/preferences
    Retorna preferências de categorias do utilizador
    """
    from backend.db import get_db

    user_id = session.get('user_id')
    db = get_db()

    prefs = db.execute(
        'SELECT category FROM preferences WHERE user_id = ?',
        (user_id,)
    ).fetchall()

    categories = [p[0] for p in prefs]

    return jsonify({'categories': categories}), 200


@categories_bp.route('/preferences', methods=['PUT'])
@require_auth
def update_preferences():
    """
    PUT /api/preferences
    Actualiza preferências de categorias do utilizador
    """
    from backend.db import get_db

    user_id = session.get('user_id')
    data = request.get_json() or {}

    # Validar que categories é uma lista
    if 'categories' not in data:
        return api_error('Campo categories é obrigatório', 'MISSING_FIELD', 400)

    if not isinstance(data['categories'], list):
        return api_error('categories deve ser uma lista', 'INVALID_FORMAT', 400)

    # Validar que cada categoria é válida
    for category in data['categories']:
        if category not in VALID_CATEGORIES:
            return api_error(f'Categoria inválida: {category}', 'INVALID_CATEGORY', 400)

    try:
        db = get_db()

        # Apagar preferências antigas
        db.execute('DELETE FROM preferences WHERE user_id = ?', (user_id,))

        # Inserir novas preferências
        for category in data['categories']:
            db.execute(
                'INSERT INTO preferences (user_id, category) VALUES (?, ?)',
                (user_id, category)
            )

        db.commit()

        return jsonify({
            'categories': data['categories'],
            'message': 'Preferências actualizadas'
        }), 200
    except Exception as e:
        db.rollback()
        return api_error(f'Erro ao actualizar: {str(e)}', 'DATABASE_ERROR', 500)
