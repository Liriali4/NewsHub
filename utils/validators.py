"""
NewsHub — Validadores de dados
Regras de validação para email, password, campos obrigatórios
"""

import re

def validate_email(email):
    """
    Valida formato de email
    Retorna True se válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Valida força da palavra-passe
    Retorna (bool, str) onde str é a mensagem de erro se inválido
    """
    if not password or len(password) < 8:
        return False, "Palavra-passe deve ter mínimo 8 caracteres"
    
    return True, ""


def validate_required_fields(data, fields):
    """
    Verifica se todos os campos obrigatórios estão presentes
    data: dicionário com os dados
    fields: lista de nomes de campos obrigatórios
    Retorna (bool, str) onde str é a mensagem de erro se inválido
    """
    for field in fields:
        if not data.get(field):
            return False, f"Campo obrigatório: {field}"
    
    return True, ""
