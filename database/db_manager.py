"""
NewsHub — Database Manager
Script para gerenciar a base de dados: init, reset, seed, backup, stats
Uso: python database/db_manager.py [init|reset|seed|backup|stats]
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys

DATABASE = 'database/newshub.db'
SCHEMA_FILE = 'database/schema.sql'


def init_db():
    """Cria as tabelas se não existirem"""
    if os.path.exists(DATABASE):
        print(f"✅ Base de dados já existe em {DATABASE}")
        return
    
    try:
        db = sqlite3.connect(DATABASE)
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        db.close()
        print(f"✅ Base de dados criada com sucesso em {DATABASE}")
    except Exception as e:
        print(f"❌ Erro ao criar base de dados: {e}")


def reset_db():
    """Apaga e recria a base de dados"""
    response = input("⚠️  Tens a certeza? Todos os dados serão apagados. (s/N): ")
    if response.lower() != 's':
        print("Cancelado.")
        return
    
    try:
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
        init_db()
        print("✅ Base de dados reposta com sucesso")
    except Exception as e:
        print(f"❌ Erro ao repor base de dados: {e}")


def seed_db():
    """Insere dados de teste"""
    import bcrypt
    
    if not os.path.exists(DATABASE):
        print(f"❌ Base de dados não existe. Cria primeiro com: python db_manager.py init")
        return
    
    try:
        db = sqlite3.connect(DATABASE)
        
        # Password de teste (password123)
        password_hash = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode('utf-8')
        
        # Inserir utilizadores de teste
        users_data = [
            ('João Silva', 'joao@example.com', password_hash),
            ('Maria Santos', 'maria@example.com', password_hash)
        ]
        
        cursor = db.cursor()
        for name, email, p_hash in users_data:
            cursor.execute(
                'INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (name, email, p_hash)
            )
        
        db.commit()
        
        # Obter IDs dos utilizadores criados
        users = db.execute('SELECT id FROM users LIMIT 2').fetchall()
        
        if len(users) >= 1:
            user_id = users[0][0]
            
            # Inserir preferências para o primeiro utilizador
            preferences_data = [
                ('tecnologia',),
                ('ciencia',),
                ('negocios',),
            ]
            
            for pref in preferences_data:
                cursor.execute(
                    'INSERT OR IGNORE INTO preferences (user_id, category) VALUES (?, ?)',
                    (user_id, pref[0])
                )
            
            # Inserir favoritos de exemplo
            articles_data = [
                ('IA revoluciona medicina', 'Inteligência artificial é agora usada em hospitais...', 'https://example.com/1', 'ciencia'),
                ('Python 3.12 lançado', 'Nova versão do Python com melhorias de performance...', 'https://example.com/2', 'tecnologia'),
                ('Startups crescem em Lisboa', 'Ecossistema de startups em Portugal atrai investimento...', 'https://example.com/3', 'negocios'),
            ]
            
            for title, desc, url, cat in articles_data:
                cursor.execute(
                    '''INSERT OR IGNORE INTO favorites 
                       (user_id, title, description, url, source_name, category) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user_id, title, desc, url, 'Fonte Teste', cat)
                )
        
        db.commit()
        db.close()
        print("✅ Dados de teste inseridos com sucesso")
        print(f"   Utilizador de teste: joao@example.com / password123")
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")


def backup_db():
    """Cria backup da base de dados"""
    if not os.path.exists(DATABASE):
        print(f"❌ Base de dados não existe")
        return
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'database/newshub_backup_{timestamp}.db'
        shutil.copy(DATABASE, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")


def stats_db():
    """Mostra estatísticas da base de dados"""
    if not os.path.exists(DATABASE):
        print(f"❌ Base de dados não existe")
        return
    
    try:
        db = sqlite3.connect(DATABASE)
        
        # Contar registos
        users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        preferences = db.execute('SELECT COUNT(*) FROM preferences').fetchone()[0]
        favorites = db.execute('SELECT COUNT(*) FROM favorites').fetchone()[0]
        
        print("📊 Estatísticas da Base de Dados")
        print(f"   Utilizadores: {users}")
        print(f"   Preferências: {preferences}")
        print(f"   Favoritos: {favorites}")
        
        # Listar utilizadores
        if users > 0:
            print("\n👥 Utilizadores:")
            user_list = db.execute('SELECT id, name, email, created_at FROM users').fetchall()
            for u_id, name, email, created in user_list:
                print(f"   #{u_id}: {name} ({email}) - criado em {created}")
        
        db.close()
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python db_manager.py [init|reset|seed|backup|stats]")
        print("\nComandos:")
        print("  init    - Cria a base de dados")
        print("  reset   - Apaga e recria a base de dados")
        print("  seed    - Insere dados de teste")
        print("  backup  - Cria backup")
        print("  stats   - Mostra estatísticas")
        return
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'reset':
        reset_db()
    elif command == 'seed':
        seed_db()
    elif command == 'backup':
        backup_db()
    elif command == 'stats':
        stats_db()
    else:
        print(f"❌ Comando desconhecido: {command}")


if __name__ == '__main__':
    main()
