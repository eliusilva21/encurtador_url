# Gera os códigos curtos aleatórios 

import secrets
import string

def gerar_codigo_curto(tamanho: int = 6) -> str:
    # Agrupa letras maiúsculas, minúsculas e números (ex: a-z, A-Z, 0-9)
    caracteres = string.ascii_letters + string.digits
    
    # Escolhe 6 caracteres aleatórios e junta em uma string só
    return ''.join(secrets.choice(caracteres) for _ in range(tamanho))