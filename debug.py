#!/usr/bin/env python3
import os
import sys
import json

print("===== DIAGNÓSTICO DE VARIÁVEIS DE AMBIENTE =====")
print(f"Python version: {sys.version}")
print(f"Diretório atual: {os.getcwd()}")
print(f"Arquivos no diretório: {os.listdir()}")
print("\nVARIÁVEIS DE AMBIENTE DISPONÍVEIS:")
for key, value in sorted(os.environ.items()):
    # Mascarar valores sensíveis para segurança
    if key in ["DATABASE_URL", "GROQ_API_KEY"] and value:
        masked_value = value[:10] + "..." if len(value) > 10 else value
        print(f"{key}: {masked_value}")
    else:
        print(f"{key}: {value}")

print("\n===== TENTANDO ACESSAR VARIÁVEIS ESPECÍFICAS =====")
db_url = os.environ.get("DATABASE_URL")
groq_key = os.environ.get("GROQ_API_KEY")

print(f"DATABASE_URL encontrado: {'SIM' if db_url else 'NÃO'}")
print(f"GROQ_API_KEY encontrado: {'SIM' if groq_key else 'NÃO'}")

print("\n===== VARIÁVEIS EM ARQUIVOS =====")
try:
    if os.path.exists(".env"):
        print("Conteúdo do arquivo .env:")
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key = line.split("=")[0]
                    print(f"  {key}: PRESENTE")
    else:
        print("Arquivo .env não encontrado")
except Exception as e:
    print(f"Erro ao ler .env: {e}")

print("\n===== FIM DO DIAGNÓSTICO =====") 