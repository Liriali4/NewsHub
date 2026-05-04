"""
NewsHub — Blueprint de Autenticação
POST /register, POST /login, POST /logout, GET /me
"""

from flask import Blueprint, request, session, jsonify
import bcrypt
from utils.validators import validate_email, validate_password, validate_required_fields
from utils.error_handlers import api_error

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def hash_password(password):
    """Hash da password com bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verifica password contra hash bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /register
    Regista novo utilizador
    """
    data = request.get_json() or {}

    # Validar campos obrigatórios
    valid, msg = validate_required_fields(data, ['name', 'email', 'password'])
    if not valid:
        return api_error(msg, 'MISSING_FIELD', 400)

    # Validar email
    if not validate_email(data['email']):
        return api_error('Email inválido', 'INVALID_EMAIL', 400)

    # Validar password
    valid, msg = validate_password(data['password'])
    if not valid:
        return api_error(msg, 'WEAK_PASSWORD', 400)

    # Verificar se email já existe
    from backend.db import get_db
    db = get_db()
    existing_user = db.execute('SELECT id FROM users WHERE email = ?', (data['email'],)).fetchone()
    if existing_user:
        return api_error('Email já registado', 'DUPLICATE_EMAIL', 409)

    # Criar utilizador
    try:
        password_hash = hash_password(data['password'])
        cursor = db.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (data['name'], data['email'], password_hash)
        )
        db.commit()
        user_id = cursor.lastrowid

        # Criar sessão
        session['user_id'] = user_id
        session.permanent = True

        return jsonify({
            'id': user_id,
            'name': data['name'],
            'email': data['email']
        }), 201
    except Exception as e:
        db.rollback()
        return api_error(f'Erro ao registar: {str(e)}', 'DATABASE_ERROR', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /login
    Login de utilizador
    """
    data = request.get_json() or {}

    # Validar campos obrigatórios
    valid, msg = validate_required_fields(data, ['email', 'password'])
    if not valid:
        return api_error('Email e palavra-passe são obrigatórios', 'MISSING_FIELD', 400)

    from backend.db import get_db
    db = get_db()

    # Procurar utilizador por email
    user = db.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (data['email'],)).fetchone()

    # Verificar credenciais (sempre retornar 401 sem especificar qual campo está errado)
    if not user or not verify_password(data['password'], user['password_hash']):
        return api_error('Credenciais inválidas', 'INVALID_CREDENTIALS', 401)

    # Actualizar último login
    try:
        db.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        db.commit()
    except Exception as e:
        db.rollback()

    # Criar sessão
    session['user_id'] = user['id']
    session.permanent = True

    return jsonify({
        'id': user['id'],
        'name': user['name'],
        'email': user['email']
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    POST /logout
    Termina sessão do utilizador
    """
    session.clear()
    return jsonify({'message': 'Sessão terminada'}), 200


@auth_bp.route('/me', methods=['GET'])
def get_me():
    """
    GET /me
    Retorna dados do utilizador autenticado
    """
    if 'user_id' not in session:
        return api_error('Não autenticado', 'UNAUTHORIZED', 401)

    from backend.db import get_db
    db = get_db()

    user = db.execute('SELECT id, name, email FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if not user:
        session.clear()
        return api_error('Utilizador não encontrado', 'NOT_FOUND', 401)

    return jsonify({
        'id': user['id'],
        'name': user['name'],
        'email': user['email']
    }), 200
