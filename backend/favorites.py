"""
NewsHub — Blueprint de Favoritos
GET/POST/DELETE /api/favorites
"""

from flask import Blueprint, request, session, jsonify
from utils.error_handlers import require_auth, api_error

favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')


@favorites_bp.route('', methods=['GET'])
@require_auth
def get_favorites():
    """
    GET /api/favorites
    Retorna todos os favoritos do utilizador
    """
    from backend.db import get_db

    user_id = session.get('user_id')
    db = get_db()

    favorites = db.execute(
        '''SELECT id, title, description, url_to_image, source_name, 
                  published_at, url, category, saved_at 
           FROM favorites 
           WHERE user_id = ? 
           ORDER BY saved_at DESC''',
        (user_id,)
    ).fetchall()

    favorites_list = [
        {
            'id': f[0],
            'title': f[1],
            'description': f[2],
            'urlToImage': f[3],
            'source': {'name': f[4]},
            'publishedAt': f[5],
            'url': f[6],
            'category': f[7],
            'saved_at': f[8]
        }
        for f in favorites
    ]

    return jsonify({'favorites': favorites_list}), 200


@favorites_bp.route('', methods=['POST'])
@require_auth
def create_favorite():
    """
    POST /api/favorites
    Adiciona um artigo aos favoritos
    """
    from backend.db import get_db

    user_id = session.get('user_id')
    data = request.get_json() or {}

    # Validar campos obrigatórios
    if not data.get('title') or not data.get('url'):
        return api_error('title e url são obrigatórios', 'MISSING_FIELD', 400)

    db = get_db()

    # Verificar se já existe
    existing = db.execute(
        'SELECT id FROM favorites WHERE user_id = ? AND url = ?',
        (user_id, data['url'])
    ).fetchone()

    if existing:
        return api_error('Artigo já nos favoritos', 'DUPLICATE', 409)

    try:
        cursor = db.execute(
            '''INSERT INTO favorites 
               (user_id, title, description, url_to_image, source_name, 
                published_at, url, category) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id,
             data.get('title'),
             data.get('description'),
             data.get('urlToImage'),
             data.get('source_name'),
             data.get('published_at'),
             data.get('url'),
             data.get('category'))
        )
        db.commit()

        favorite = {
            'id': cursor.lastrowid,
            'title': data.get('title'),
            'description': data.get('description'),
            'urlToImage': data.get('urlToImage'),
            'source': {'name': data.get('source_name')},
            'publishedAt': data.get('published_at'),
            'url': data.get('url'),
            'category': data.get('category')
        }

        return jsonify(favorite), 201
    except Exception as e:
        db.rollback()
        return api_error(f'Erro ao adicionar: {str(e)}', 'DATABASE_ERROR', 500)


@favorites_bp.route('/<int:favorite_id>', methods=['DELETE'])
@require_auth
def delete_favorite(favorite_id):
    """
    DELETE /api/favorites/<id>
    Remove um artigo dos favoritos
    """
    from backend.db import get_db

    user_id = session.get('user_id')
    db = get_db()

    # Verificar que existe e pertence ao utilizador
    favorite = db.execute(
        'SELECT id FROM favorites WHERE id = ? AND user_id = ?',
        (favorite_id, user_id)
    ).fetchone()

    if not favorite:
        return api_error('Favorito não encontrado', 'NOT_FOUND', 404)

    try:
        db.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
        db.commit()

        return jsonify({'message': 'Removido dos favoritos'}), 200
    except Exception as e:
        db.rollback()
        return api_error(f'Erro ao remover: {str(e)}', 'DATABASE_ERROR', 500)
