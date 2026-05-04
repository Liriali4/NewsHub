"""
NewsHub — Testes de Rotas
Script para testar todas as rotas do backend manualmente
Uso: python tests/test_routes.py
"""

import requests
import json
import sys
import os

# Adicionar o diretório root ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = 'http://localhost:5000/api'
SESSION = requests.Session()

# Contador de testes
TESTS_PASSED = 0
TESTS_FAILED = 0

TEST_USER = {
    'name': 'Teste User',
    'email': f'teste_{int(os.times()[4]*1000)}@example.com',
    'password': 'password123'
}


def print_test_result(test_num, test_name, passed, response=None):
    """Imprime resultado do teste"""
    global TESTS_PASSED, TESTS_FAILED
    
    status = "✅ PASSOU" if passed else "❌ FALHOU"
    print(f"{test_num:2d}. {test_name:40s} {status}")
    
    if not passed and response is not None:
        try:
            data = response.json()
            print(f"    Resposta: {data}")
        except:
            print(f"    Status: {response.status_code}, Texto: {response.text[:100]}")
    
    if passed:
        TESTS_PASSED += 1
    else:
        TESTS_FAILED += 1


def test_1_health_check():
    """1. GET /health"""
    try:
        r = SESSION.get(f'{BASE_URL}/health')
        passed = r.status_code == 200 and r.json().get('status') == 'ok'
        print_test_result(1, "GET /health", passed, r if not passed else None)
    except Exception as e:
        print_test_result(1, "GET /health", False)
        print(f"    Erro: {e}")


def test_2_register_success():
    """2. POST /register - Sucesso"""
    try:
        r = SESSION.post(f'{BASE_URL}/auth/register', json=TEST_USER)
        passed = r.status_code == 201 and r.json().get('id')
        print_test_result(2, "POST /auth/register - Sucesso", passed, r if not passed else None)
    except Exception as e:
        print_test_result(2, "POST /auth/register - Sucesso", False)
        print(f"    Erro: {e}")


def test_3_register_duplicate_email():
    """3. POST /register - Email duplicado"""
    try:
        r = SESSION.post(f'{BASE_URL}/auth/register', json=TEST_USER)
        passed = r.status_code == 409
        print_test_result(3, "POST /auth/register - Email duplicado", passed, r if not passed else None)
    except Exception as e:
        print_test_result(3, "POST /auth/register - Email duplicado", False)
        print(f"    Erro: {e}")


def test_4_login_success():
    """4. POST /login - Sucesso"""
    try:
        r = SESSION.post(f'{BASE_URL}/auth/login', json={
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        })
        passed = r.status_code == 200 and r.json().get('id')
        print_test_result(4, "POST /auth/login - Sucesso", passed, r if not passed else None)
    except Exception as e:
        print_test_result(4, "POST /auth/login - Sucesso", False)
        print(f"    Erro: {e}")


def test_5_login_wrong_password():
    """5. POST /login - Password errada"""
    try:
        r = SESSION.post(f'{BASE_URL}/auth/login', json={
            'email': TEST_USER['email'],
            'password': 'wrongpassword'
        })
        passed = r.status_code == 401
        print_test_result(5, "POST /auth/login - Password errada", passed, r if not passed else None)
    except Exception as e:
        print_test_result(5, "POST /auth/login - Password errada", False)
        print(f"    Erro: {e}")


def test_6_get_me():
    """6. GET /auth/me - Autenticado"""
    try:
        r = SESSION.get(f'{BASE_URL}/auth/me')
        passed = r.status_code == 200 and r.json().get('id')
        print_test_result(6, "GET /auth/me - Autenticado", passed, r if not passed else None)
    except Exception as e:
        print_test_result(6, "GET /auth/me - Autenticado", False)
        print(f"    Erro: {e}")


def test_7_get_news():
    """7. GET /news?category=geral&page=1"""
    try:
        r = SESSION.get(f'{BASE_URL}/news?category=geral&page=1')
        passed = r.status_code == 200 and isinstance(r.json().get('articles'), list)
        print_test_result(7, "GET /news - Carregamento básico", passed, r if not passed else None)
    except Exception as e:
        print_test_result(7, "GET /news - Carregamento básico", False)
        print(f"    Erro: {e}")


def test_8_get_preferences_empty():
    """8. GET /preferences - Vazio"""
    try:
        r = SESSION.get(f'{BASE_URL}/preferences')
        passed = r.status_code == 200 and isinstance(r.json().get('categories'), list)
        print_test_result(8, "GET /preferences - Vazio", passed, r if not passed else None)
    except Exception as e:
        print_test_result(8, "GET /preferences - Vazio", False)
        print(f"    Erro: {e}")


def test_9_save_preferences():
    """9. PUT /preferences"""
    try:
        r = SESSION.put(f'{BASE_URL}/preferences', json={
            'categories': ['tecnologia', 'ciencia']
        })
        passed = r.status_code == 200 and 'tecnologia' in r.json().get('categories', [])
        print_test_result(9, "PUT /preferences - Guardar", passed, r if not passed else None)
    except Exception as e:
        print_test_result(9, "PUT /preferences - Guardar", False)
        print(f"    Erro: {e}")


def test_10_get_preferences_saved():
    """10. GET /preferences - Com dados guardados"""
    try:
        r = SESSION.get(f'{BASE_URL}/preferences')
        passed = r.status_code == 200 and 'tecnologia' in r.json().get('categories', [])
        print_test_result(10, "GET /preferences - Com dados", passed, r if not passed else None)
    except Exception as e:
        print_test_result(10, "GET /preferences - Com dados", False)
        print(f"    Erro: {e}")


def test_11_add_favorite():
    """11. POST /favorites"""
    try:
        favorite_data = {
            'title': 'Artigo de Teste',
            'description': 'Descrição de teste',
            'url': 'https://example.com/test-article',
            'source_name': 'Fonte Teste',
            'category': 'tecnologia'
        }
        r = SESSION.post(f'{BASE_URL}/favorites', json=favorite_data)
        passed = r.status_code == 201 and r.json().get('id')
        print_test_result(11, "POST /favorites - Adicionar", passed, r if not passed else None)
    except Exception as e:
        print_test_result(11, "POST /favorites - Adicionar", False)
        print(f"    Erro: {e}")


def test_12_get_favorites():
    """12. GET /favorites"""
    try:
        r = SESSION.get(f'{BASE_URL}/favorites')
        passed = r.status_code == 200 and isinstance(r.json().get('favorites'), list) and len(r.json().get('favorites', [])) > 0
        print_test_result(12, "GET /favorites - Listar", passed, r if not passed else None)
    except Exception as e:
        print_test_result(12, "GET /favorites - Listar", False)
        print(f"    Erro: {e}")


def test_13_logout():
    """13. POST /logout"""
    try:
        r = SESSION.post(f'{BASE_URL}/auth/logout')
        passed = r.status_code == 200
        print_test_result(13, "POST /auth/logout", passed, r if not passed else None)
    except Exception as e:
        print_test_result(13, "POST /auth/logout", False)
        print(f"    Erro: {e}")


def test_14_get_me_unauthenticated():
    """14. GET /auth/me - Não autenticado"""
    try:
        r = SESSION.get(f'{BASE_URL}/auth/me')
        passed = r.status_code == 401
        print_test_result(14, "GET /auth/me - Desautenticado", passed, r if not passed else None)
    except Exception as e:
        print_test_result(14, "GET /auth/me - Desautenticado", False)
        print(f"    Erro: {e}")


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("NewsHub — Testes de Rotas")
    print("="*60 + "\n")
    
    print("Ambiente de Teste:")
    print(f"  URL Base: {BASE_URL}")
    print(f"  Email de Teste: {TEST_USER['email']}\n")
    
    # Executar testes
    test_1_health_check()
    test_2_register_success()
    test_3_register_duplicate_email()
    test_4_login_success()
    test_5_login_wrong_password()
    test_6_get_me()
    test_7_get_news()
    test_8_get_preferences_empty()
    test_9_save_preferences()
    test_10_get_preferences_saved()
    test_11_add_favorite()
    test_12_get_favorites()
    test_13_logout()
    test_14_get_me_unauthenticated()
    
    # Resumo
    print("\n" + "="*60)
    print(f"RESUMO: {TESTS_PASSED}/14 testes passaram")
    if TESTS_FAILED == 0:
        print("✅ Todos os testes passaram!")
    else:
        print(f"❌ {TESTS_FAILED} testes falharam")
    print("="*60 + "\n")
    
    return 0 if TESTS_FAILED == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
