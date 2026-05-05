"""
NewsHub — Flask Application
Aplicação principal, CORS, configuração de sessões
"""

from flask import Flask, jsonify, session, request
from flask_cors import CORS
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__)

# === CONFIGURAÇÃO ===
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-desenvolvimento-insegura-mudar-producao')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # True only in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['CORS_ORIGINS'] = [
    'http://localhost:3000',
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'file://'
]

# === CORS ===
CORS(app,
     origins=['http://localhost:3000', 'http://localhost:5500', 'http://127.0.0.1:5500', 'file://'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type'],
     supports_credentials=True)

# === DATABASE ===
from backend.db import init_db_app, get_db
init_db_app(app)

# === BLUEPRINTS ===
from backend.auth import auth_bp
from backend.news import news_bp
from backend.categories import categories_bp
from backend.favorites import favorites_bp

app.register_blueprint(auth_bp)
app.register_blueprint(news_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(favorites_bp)

# === ROTAS ===

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/api/ai/summary', methods=['POST'])
def get_summary():
    """
    POST /api/ai/summary
    Gera resumo inteligente com IA
    """
    from utils.ai_features import generate_summary
    
    data = request.get_json() or {}
    
    if not data.get('title') or not data.get('description'):
        return jsonify({
            'error': 'title e description são obrigatórios',
            'code': 'MISSING_FIELD'
        }), 400

    try:
        summary = generate_summary(
            data.get('title'),
            data.get('description'),
            data.get('content')
        )
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar resumo',
            'code': 'AI_ERROR'
        }), 500


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Recurso não encontrado',
        'code': 'NOT_FOUND'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'code': 'INTERNAL_ERROR'
    }), 500


# === MAIN ===

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='localhost', port=5000)
