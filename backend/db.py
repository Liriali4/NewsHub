"""
NewsHub — Database Connection and Initialization
Gestão de conexões SQLite e inicialização da BD
"""

import sqlite3
import os
from flask import g

DATABASE = 'database/newshub.db'


def get_db():
    """
    Retorna conexão à base de dados
    Reutiliza conexão existente no contexto da requisição
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_db(e=None):
    """
    Fecha a conexão à base de dados
    Chamada automaticamente ao fim da requisição
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """
    Inicializa a base de dados, criando as tabelas se não existirem
    Executa o ficheiro database/schema.sql
    """
    db = sqlite3.connect(DATABASE)
    
    # Ler e executar schema
    schema_path = 'database/schema.sql'
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
    
    db.commit()
    db.close()


def init_db_app(app):
    """
    Regista as funções de inicialização/encerramento da BD na app Flask
    """
    app.teardown_appcontext(close_db)
    
    # Inicializar BD na primeira requisição se não existir
    with app.app_context():
        if not os.path.exists(DATABASE):
            init_db()
