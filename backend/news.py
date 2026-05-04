"""
NewsHub — Blueprint de Notícias
GET /api/news — carregamento de notícias com paginação e filtros
"""

from flask import Blueprint, request, jsonify, session
import requests
from utils.error_handlers import require_auth, api_error
import time

news_bp = Blueprint('news', __name__, url_prefix='/api')

# Mapeamento de categorias português → inglês
CATEGORY_MAP = {
    "tecnologia": "technology",
    "desporto": "sports",
    "saude": "health",
    "ciencia": "science",
    "negocios": "business",
    "entretenimento": "entertainment",
    "geral": "general"
}

# Cache simples em memória com TTL
_news_cache = {}
_CACHE_TTL = 300  # 5 minutos


def get_news_from_api(category, page, query, api_key):
    """
    Faz pedido à NewsAPI.org
    """
    base_url = "https://newsapi.org/v2/top-headlines"
    
    params = {
        'apiKey': api_key,
        'page': page,
        'pageSize': 12,
        'language': 'en'
    }

    if category and category != 'geral':
        params['category'] = CATEGORY_MAP.get(category, 'general')
    else:
        params['category'] = 'general'

    if query:
        params['q'] = query
        base_url = "https://newsapi.org/v2/everything"
        params.pop('language', None)

    try:
        response = requests.get(base_url, params=params, timeout=5)
        
        if response.status_code == 401:
            return None, "API_KEY_INVALID"
        elif response.status_code == 429:
            return None, "RATE_LIMIT"
        elif response.status_code != 200:
            return None, "API_ERROR"

        data = response.json()
        return data, None
    except requests.Timeout:
        return None, "TIMEOUT"
    except Exception as e:
        return None, "CONNECTION_ERROR"


def clean_articles(articles):
    """
    Limpa e normaliza artigos
    """
    cleaned = []
    seen_urls = set()

    for article in articles:
        # Pular artigos removidos ou sem título
        if not article.get('title') or article['title'] == "[Removed]":
            continue
        if not article.get('description') or article['description'] == "[Removed]":
            continue

        # Evitar duplicados
        url = article.get('url')
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Truncar descrição
        description = article.get('description', '')[:200]

        cleaned.append({
            'id': hash(url) & 0x7fffffff,  # id positivo
            'title': article['title'],
            'description': description,
            'urlToImage': article.get('urlToImage') or None,
            'source': {
                'name': article.get('source', {}).get('name', 'Desconhecido')
            },
            'publishedAt': article.get('publishedAt'),
            'url': url,
            'category': CATEGORY_MAP.get('geral', 'general'),
            'isFavorite': False
        })

    return cleaned


@news_bp.route('/news', methods=['GET'])
def get_news():
    """
    GET /api/news?category=X&page=Y&q=Z
    Carrega notícias com paginação e filtragem
    """
    import os
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        return api_error('Chave de API não configurada', 'NO_API_KEY', 503)

    category = request.args.get('category', 'geral')
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')

    # Validar paginação
    if page < 1:
        page = 1

    # Tentar cache com TTL
    cache_key = f"news:{category}:{page}:{query}"
    if cache_key in _news_cache:
        cached_data, timestamp = _news_cache[cache_key]
        if time.time() - timestamp < _CACHE_TTL:
            cached_data['_cached'] = True
            return jsonify(cached_data), 200
        else:
            del _news_cache[cache_key]  # Remover cache expirado

    # Buscar da API
    data, error = get_news_from_api(category, page, query, api_key)

    if error:
        if error == "API_KEY_INVALID":
            return api_error('Serviço de notícias indisponível', 'API_KEY_INVALID', 503)
        elif error == "RATE_LIMIT":
            return api_error('Limite de pedidos atingido. Tenta em breve.', 'RATE_LIMIT', 429)
        elif error == "TIMEOUT":
            return api_error('Tempo de resposta excedido', 'TIMEOUT', 504)
        else:
            return api_error('Erro ao carregar notícias', error, 503)

    # Processar artigos
    articles = clean_articles(data.get('articles', []))
    total_results = data.get('totalResults', 0)
    has_more = total_results > (page * 12)

    response_data = {
        'articles': articles,
        'totalResults': total_results,
        'page': page,
        'hasMore': has_more
    }

    # Cache com TTL
    _news_cache[cache_key] = (response_data, time.time())

    return jsonify(response_data), 200


@news_bp.route('/news/personalized', methods=['GET'])
@require_auth
def get_personalized_news():
    """
    GET /api/news/personalized
    Retorna notícias personalizadas baseadas nas preferências do utilizador
    """
    from backend.db import get_db
    import os

    user_id = session.get('user_id')
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        return api_error('Chave de API não configurada', 'NO_API_KEY', 503)

    # Carregar preferências do utilizador
    db = get_db()
    preferences = db.execute(
        'SELECT category FROM preferences WHERE user_id = ? LIMIT 6',
        (user_id,)
    ).fetchall()

    if not preferences:
        return jsonify({
            'articles': [],
            'personalized': False,
            'message': 'Define as tuas preferências para ver conteúdo personalizado'
        }), 200

    # Buscar notícias para cada categoria preferida
    all_articles = []
    categories_used = []

    for pref in preferences:
        category = pref[0]
        categories_used.append(category)
        
        data, error = get_news_from_api(category, 1, '', api_key)
        if data and not error:
            articles = clean_articles(data.get('articles', [])[:3])
            all_articles.extend(articles)

    # Limitar aos primeiros 12 e misturar
    all_articles = all_articles[:12]

    return jsonify({
        'articles': all_articles,
        'personalized': True,
        'based_on': categories_used
    }), 200
