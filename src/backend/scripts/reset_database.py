#!/usr/bin/env python
"""
Script para resetar completamente o banco de dados.
USO: python reset_database.py
AVISO: Isso APAGA TODOS os dados permanentemente!
"""

import os
import sys
import django
from pathlib import Path

# Configura o Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from pathlib import Path

def reset_database():
    """Remove o arquivo do banco SQLite e recria as tabelas vazias"""
    
    print("=" * 60)
    print("RESETANDO BANCO DE DADOS - SISTEMA DE CHAMADA")
    print("=" * 60)
    
    # 1. Localiza o arquivo do banco
    db_path = Path(__file__).resolve().parent.parent / 'db.sqlite3'
    
    if not db_path.exists():
        print("ERRO: Banco de dados nao encontrado!")
        return False
    
    # 2. Confirmação de segurança
    print(f"\nATENCAO: Isso vai APAGAR o arquivo:")
    print(f"   {db_path}")
    print(f"\nTamanho atual: {db_path.stat().st_size / 1024:.2f} KB")
    
    resposta = input("\nTem certeza? Digite 'SIM' para continuar: ")
    if resposta.upper() != 'SIM':
        print("Operacao cancelada.")
        return False
    
    # 3. Fecha conexões do Django
    print("\nFechando conexoes do Django...")
    connection.close()
    
    # 4. Remove o arquivo do banco
    try:
        db_path.unlink()
        print("SUCESSO: Arquivo db.sqlite3 removido.")
    except Exception as e:
        print(f"ERRO ao remover arquivo: {e}")
        return False
    
    # 5. Recria as tabelas (migrações)
    print("\nAplicando migracoes...")
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate'])
        print("SUCESSO: Migracoes aplicadas.")
    except Exception as e:
        print(f"ERRO nas migracoes: {e}")
        return False
    
    # 6. Cria superusuário admin padrão
    print("\nCriando superusuario padrao...")
    try:
        # Remove usuário admin se existir
        User.objects.filter(username='admin').delete()
        
        # Cria novo admin
        User.objects.create_superuser(
            username='admin',
            email='admin@ifb.edu.br',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        print("SUCESSO: Superusuario criado:")
        print("   Usuario: admin")
        print("   Senha: admin123")
        print("   Email: admin@ifb.edu.br")
        
    except Exception as e:
        print(f"AVISO: Nao foi possivel criar superusuario: {e}")
    
    print("\n" + "=" * 60)
    print("SUCESSO: BANCO DE DADOS RESETADO!")
    print("=" * 60)
    
    # 7. Informações importantes
    print("\nPROXIMOS PASSOS:")
    print("   1. Execute: python scripts/populate_demo.py")
    print("   2. Ou: python scripts/populate_test.py")
    print("\nURLs do sistema:")
    print("   Admin: http://127.0.0.1:8000/admin/")
    print("   API Docs: http://127.0.0.1:8000/api/schema/swagger/")
    print("   Login admin: admin / admin123")
    
    return True

if __name__ == '__main__':
    reset_database()