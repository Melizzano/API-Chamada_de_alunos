# Crie um arquivo check_api.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoint(endpoint, method="GET", data=None, token=None):
    """Testa um endpoint da API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f"Token {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, data=json.dumps(data))
        elif method == "PUT":
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, headers=headers, data=json.dumps(data))
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"{method} {endpoint}: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"   ERRO: {response.text[:200]}")
        
        return response
        
    except Exception as e:
        print(f"{method} {endpoint}: ERRO - {str(e)}")
        return None

def main():
    print("=" * 60)
    print("VERIFICAÇÃO DA API - SISTEMA DE CHAMADA DE ALUNOS")
    print("=" * 60)
    
    # Primeiro, vamos obter um token (use um dos tokens gerados)
    # Substitua pelo token real do admin
    ADMIN_TOKEN = input("Digite o token do admin (ou pressione Enter para usar o do script): ").strip()
    
    if not ADMIN_TOKEN:
        # Obter token do banco (se disponível)
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        
        try:
            admin_user = User.objects.get(username='admin')
            token_obj = Token.objects.get(user=admin_user)
            ADMIN_TOKEN = token_obj.key
            print(f"Usando token do admin: {ADMIN_TOKEN[:20]}...")
        except:
            print("⚠️ Token não encontrado. Execute populate_db.py primeiro.")
            return
    
    print("\n1. Testando endpoints públicos...")
    test_endpoint("/turmas-ativas/")
    test_endpoint("/professores-publicos/")
    
    print("\n2. Testando endpoints protegidos sem token...")
    test_endpoint("/professores/")
    test_endpoint("/alunos/")
    
    print("\n3. Testando endpoints com token de admin...")
    
    # Listar
    response = test_endpoint("/professores/", token=ADMIN_TOKEN)
    if response and response.status_code == 200:
        professores = response.json()
        if len(professores) > 0:
            professor_id = professores[0]['id']
            print(f"   Professor ID encontrado: {professor_id}")
            
            # Testar endpoint específico do professor
            test_endpoint(f"/professores/{professor_id}/turmas/", token=ADMIN_TOKEN)
    
    response = test_endpoint("/turmas/", token=ADMIN_TOKEN)
    if response and response.status_code == 200:
        turmas = response.json()
        if len(turmas) > 0:
            turma_id = turmas[0]['id']
            print(f"   Turma ID encontrado: {turma_id}")
            
            # Testar endpoints da turma
            test_endpoint(f"/turmas/{turma_id}/alunos/", token=ADMIN_TOKEN)
            test_endpoint(f"/turmas/{turma_id}/representante/", token=ADMIN_TOKEN)
            test_endpoint(f"/turmas/{turma_id}/dashboard/", token=ADMIN_TOKEN)
    
    response = test_endpoint("/alunos/", token=ADMIN_TOKEN)
    if response and response.status_code == 200:
        alunos = response.json()
        if len(alunos) > 0:
            aluno_id = alunos[0]['id']
            print(f"   Aluno ID encontrado: {aluno_id}")
    
    print("\n4. Testando criação de dados...")
    
    # Criar um novo professor
    novo_professor = {
        "nome": "Prof. Teste API",
        "email": "teste.api@edutrack.com",
        "departamento": "Testes",
        "ativo": True
    }
    
    response = test_endpoint("/professores/", "POST", novo_professor, ADMIN_TOKEN)
    
    print("\n5. Testando matrícula...")
    if 'turma_id' in locals() and 'aluno_id' in locals():
        data_matricula = {"aluno_id": aluno_id}
        test_endpoint(f"/turmas/{turma_id}/matricular-aluno/", "POST", data_matricula, ADMIN_TOKEN)
    
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO CONCLUÍDA!")
    print("=" * 60)
    
    # Mostrar estatísticas
    try:
        from app.models import Professor, Aluno, Turma, Matricula, Presenca
        
        print("\n📊 ESTATÍSTICAS DO BANCO:")
        print(f"   Professores: {Professor.objects.count()}")
        print(f"   Alunos: {Aluno.objects.count()}")
        print(f"   Turmas: {Turma.objects.count()}")
        print(f"   Matrículas: {Matricula.objects.count()}")
        print(f"   Presenças: {Presenca.objects.count()}")
        
    except Exception as e:
        print(f"\n⚠️ Não foi possível obter estatísticas: {str(e)}")

if __name__ == '__main__':
    main()