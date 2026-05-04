"""
NewsHub — Funcionalidades de IA
Resumos inteligentes, análise de sentimento, recomendações
"""

import os
from dotenv import load_dotenv

load_dotenv()

AI_ENABLED = os.getenv('AI_ENABLED', 'false').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')


def generate_summary(title: str, description: str, content: str = None) -> dict:
    """
    Gera resumo inteligente de um artigo
    Tenta com IA primeiro, fallback para extractive summary se falhar ou IA desactivada
    
    Retorna:
    {
        'summary': 'texto de 2-3 frases',
        'source': 'openai' ou 'extractive',
        'model': 'gpt-3.5-turbo' ou 'none'
    }
    """
    
    # Modo IA (OpenAI)
    if AI_ENABLED and OPENAI_API_KEY:
        try:
            import openai
            
            openai.api_key = OPENAI_API_KEY
            
            prompt_text = f"Resume esta notícia em 2-3 frases em português:\nTítulo: {title}\nDescrição: {description}"
            
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "És um assistente que cria resumos concisos de notícias em português europeu. Responde sempre em 2-3 frases directas, sem introduções."
                    },
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ],
                temperature=0.7,
                max_tokens=150,
                timeout=8
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            return {
                'summary': summary_text,
                'source': 'openai',
                'model': AI_MODEL
            }
        except Exception as e:
            print(f"Erro ao chamar OpenAI: {e}")
            # Fallback para extractive
    
    # Modo fallback (extractive)
    return {
        'summary': _extractive_summary(description),
        'source': 'extractive',
        'model': 'none'
    }


def _extractive_summary(text: str) -> str:
    """
    Extrai as primeiras 2 frases do texto como resumo
    """
    if not text:
        return 'Resumo não disponível.'
    
    # Dividir por ponto e retornar primeiras 2 frases
    sentences = text.split('. ')
    if len(sentences) >= 2:
        return sentences[0] + '. ' + sentences[1] + '.'
    elif len(sentences) == 1:
        return sentences[0] + '.'
    else:
        return text[:200] + '...'


def analyze_sentiment(title: str, description: str) -> dict:
    """
    Analisa sentimento de um artigo (POSITIVO, NEGATIVO, NEUTRO)
    
    Retorna:
    {
        'sentiment': 'POSITIVO' | 'NEGATIVO' | 'NEUTRO',
        'justification': 'breve explicação',
        'confidence': 0.0-1.0,
        'source': 'openai' ou 'keyword'
    }
    """
    
    if AI_ENABLED and OPENAI_API_KEY:
        try:
            import openai
            
            openai.api_key = OPENAI_API_KEY
            
            prompt_text = f"Classifica o sentimento desta notícia como POSITIVO, NEGATIVO ou NEUTRO. Responde em português.\nTítulo: {title}\nDescrição: {description}"
            
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Classifica o sentimento de notícias. Responde apenas com uma palavra (POSITIVO, NEGATIVO ou NEUTRO) seguida de um ponto e uma breve justificação de 1 frase em português."
                    },
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ],
                temperature=0.5,
                max_tokens=100,
                timeout=8
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse da resposta
            if 'POSITIVO' in response_text.upper():
                sentiment = 'POSITIVO'
            elif 'NEGATIVO' in response_text.upper():
                sentiment = 'NEGATIVO'
            else:
                sentiment = 'NEUTRO'
            
            justification = response_text.split('. ', 1)[-1] if '. ' in response_text else response_text
            
            return {
                'sentiment': sentiment,
                'justification': justification,
                'confidence': 0.85,
                'source': 'openai'
            }
        except Exception as e:
            print(f"Erro ao chamar OpenAI para sentimento: {e}")
    
    # Fallback com análise de palavras-chave
    return _keyword_sentiment_analysis(title, description)


def _keyword_sentiment_analysis(title: str, description: str) -> dict:
    """
    Análise de sentimento baseada em palavras-chave em português
    """
    positive_words = [
        'sucesso', 'inovação', 'crescimento', 'avanço', 'ganho', 'vitória',
        'excelente', 'bom', 'ótimo', 'melhor', 'positivo', 'esperança',
        'alegria', 'oportunidade', 'benefício'
    ]
    
    negative_words = [
        'crise', 'queda', 'fracasso', 'morte', 'acidente', 'risco',
        'perda', 'problema', 'erro', 'falha', 'ruim', 'péssimo',
        'nefasto', 'desastre', 'catástrofe', 'destruição'
    ]
    
    text = (title + ' ' + description).lower()
    
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    if positive_count > negative_count:
        sentiment = 'POSITIVO'
    elif negative_count > positive_count:
        sentiment = 'NEGATIVO'
    else:
        sentiment = 'NEUTRO'
    
    return {
        'sentiment': sentiment,
        'justification': f'Análise de {positive_count} palavras positivas e {negative_count} do tipo negativo.',
        'confidence': 0.5,
        'source': 'keyword'
    }


def get_recommendations(user_categories: list, favorite_titles: list, available_articles: list) -> list:
    """
    Recomenda artigos baseado em preferências e favoritos do utilizador
    
    Retorna lista de objetos com:
    {
        'article': {...},
        'score': número,
        'reason': 'explicação da recomendação'
    }
    """
    
    recommendations = []
    
    for article in available_articles:
        score = 0
        reasons = []
        
        # +3 se categoria está nas preferências
        if article.get('category') in user_categories:
            score += 3
            reasons.append('na tua categoria preferida')
        
        # +1 para cada palavra do título que coincide com favoritos
        if favorite_titles:
            favorite_keywords = ' '.join(favorite_titles).lower().split()
            article_keywords = article.get('title', '').lower().split()
            matches = sum(1 for kw in article_keywords if kw in favorite_keywords)
            if matches > 0:
                score += matches
                reasons.append(f'relacionado com {matches} dos teus favoritos')
        
        recommendations.append({
            'article': article,
            'score': score,
            'reason': ' | '.join(reasons) if reasons else 'Artigo recomendado'
        })
    
    # Ordenar por score decrescente e limitar a top 5
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:5]


def classify_category(title: str, description: str) -> dict:
    """
    Classifica um artigo numa das 6 categorias fixas
    
    Retorna:
    {
        'category': 'tecnologia' | 'desporto' | ...,
        'confidence': 0.0-1.0,
        'source': 'openai' ou 'keyword'
    }
    """
    
    valid_categories = [
        'tecnologia', 'desporto', 'saude', 'ciencia', 'negocios', 'entretenimento'
    ]
    
    if AI_ENABLED and OPENAI_API_KEY:
        try:
            import openai
            
            openai.api_key = OPENAI_API_KEY
            
            prompt_text = f"Classifica este artigo numa das seguintes categorias: {', '.join(valid_categories)}.\nTítulo: {title}\nDescrição: {description}"
            
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"Classifica artigos em português em uma destas categorias: {', '.join(valid_categories)}. Responde apenas com a categoria."
                    },
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ],
                temperature=0.3,
                max_tokens=30,
                timeout=8
            )
            
            category_response = response.choices[0].message.content.strip().lower()
            
            # Encontrar a categoria mais próxima
            for cat in valid_categories:
                if cat in category_response:
                    return {
                        'category': cat,
                        'confidence': 0.9,
                        'source': 'openai'
                    }
            
            return {
                'category': 'geral',
                'confidence': 0.3,
                'source': 'openai'
            }
        except Exception as e:
            print(f"Erro ao chamar OpenAI para classificação: {e}")
    
    # Fallback com análise de palavras-chave
    return _keyword_classification(title, description)


def _keyword_classification(title: str, description: str) -> dict:
    """
    Classificação de artigos por palavras-chave
    """
    
    keywords = {
        'tecnologia': ['software', 'hardware', 'programação', 'ia', 'código', 'app', 'digital', 'tech', 'computador', 'internet'],
        'desporto': ['futebol', 'jogo', 'equipa', 'jogador', 'desporto', 'campeonato', 'golo', 'atleta', 'vitória', 'derrota'],
        'saude': ['saúde', 'doença', 'médico', 'hospital', 'medicina', 'cura', 'tratamento', 'paciente', 'sintoma', 'saúde'],
        'ciencia': ['investigação', 'ciência', 'estudo', 'pesquisa', 'descoberta', 'cientista', 'experimento', 'físico', 'química', 'biologia'],
        'negocios': ['empresa', 'negócio', 'economia', 'bolsa', 'mercado', 'lucro', 'investimento', 'venda', 'comércio', 'financeiro'],
        'entretenimento': ['filme', 'música', 'série', 'ator', 'artista', 'diversão', 'show', 'cinema', 'televição', 'jogo']
    }
    
    text = (title + ' ' + description).lower()
    
    best_category = 'tecnologia'
    best_score = 0
    
    for category, words in keywords.items():
        score = sum(1 for word in words if word in text)
        if score > best_score:
            best_score = score
            best_category = category
    
    confidence = min(0.95, 0.3 + (best_score * 0.1))
    
    return {
        'category': best_category,
        'confidence': confidence,
        'source': 'keyword'
    }
