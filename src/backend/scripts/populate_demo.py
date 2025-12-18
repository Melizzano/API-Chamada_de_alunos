#!/usr/bin/env python
"""
Popula o banco com dados RICOS para demonstracao IFB.
Dados especificos e realistas para o IFB Campus Estrutural.
"""

import os
import sys
import django
from pathlib import Path
from datetime import date, timedelta
import random

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group
from app.models import Professor, Aluno, Turma, Matricula, Presenca


def criar_grupos_permissoes():
    print("Criando grupos de usuarios...")

    grupos_nomes = ['Administradores', 'Professores', 'Alunos']

    for nome_grupo in grupos_nomes:
        Group.objects.get_or_create(name=nome_grupo)

    return grupos_nomes


def criar_professores():
    print("\nCriando professores IFB...")

    professores = [
        {
            'nome': 'Prof. Dr. Marcelo Costa',
            'email': 'marcelo.costa@IFBpython.com',
            'departamento': 'Tecnologia da Informacao',
            'username': 'marcelo.costa',
            'password': 'prof123',
            'titulacao': 'Doutor em Ciencia da Computacao'
        },
        {
            'nome': 'Prof. Dra. Fernanda Lima',
            'email': 'fernanda.lima@IFBpython.com',
            'departamento': 'Matematica Aplicada',
            'username': 'fernanda.lima',
            'password': 'prof123',
            'titulacao': 'Doutora em Matematica'
        },
        {
            'nome': 'Prof. Ms. Roberto Alves',
            'email': 'roberto.alves@IFBpython.com',
            'departamento': 'Estatistica',
            'username': 'roberto.alves',
            'password': 'prof123',
            'titulacao': 'Mestre em Estatistica'
        },
        {
            'nome': 'Prof. Dra. Camila Santos',
            'email': 'camila.santos@IFBpython.com',
            'departamento': 'Engenharia de Software',
            'username': 'camila.santos',
            'password': 'prof123',
            'titulacao': 'Doutora em Engenharia de Software'
        },
        {
            'nome': 'Prof. Esp. Pedro Oliveira',
            'email': 'pedro.oliveira@IFBpython.com',
            'departamento': 'Banco de Dados',
            'username': 'pedro.oliveira',
            'password': 'prof123',
            'titulacao': 'Especialista em Banco de Dados'
        },
        {
            'nome': 'Prof. Esp. Wellyelton Gualberto de Brito Rodrigues',
            'email': 'wellyelton.rodrigues@ifb.edu.br',
            'departamento': 'Desenvolvimento de Software com Formação BackEnd - Python com Django',
            'username': 'wellyelton.rodrigues',
            'password': 'prof123',
            'titulacao': 'Especialista em Desenvolvimento BackEnd com Python e Django'
        }
    ]

    grupo_prof = Group.objects.get(name='Professores')
    prof_objects = []

    for dados in professores:
        user, _ = User.objects.get_or_create(
            username=dados['username'],
            defaults={
                'email': dados['email'],
                'first_name': dados['nome'].split()[1],
                'last_name': ' '.join(dados['nome'].split()[2:])
            }
        )
        user.set_password(dados['password'])
        user.save()
        user.groups.add(grupo_prof)

        prof, _ = Professor.objects.get_or_create(
            usuario=user,
            defaults={
                'nome': dados['nome'],
                'email': dados['email'],
                'departamento': dados['departamento'],
                'ativo': True
            }
        )

        prof_objects.append(prof)
        print(f"   {dados['titulacao']} - {dados['nome']}")

    return prof_objects


def criar_alunos():
    print("\nCriando alunos IFB...")

    nomes_masculinos = [
        'Lucas', 'Mateus', 'Gabriel', 'Pedro', 'Rafael', 'Felipe',
        'Bruno', 'Daniel', 'Andre', 'Carlos', 'Joao', 'Marcos',
        'Thiago', 'Leonardo', 'Vinicius', 'Eduardo', 'Caio', 'Igor',
        'Renan', 'Diego', 'Hugo', 'Samuel', 'Alexandre', 'Rodrigo', 'Matheus'
    ]

    nomes_femininos = [
        'Ana', 'Julia', 'Maria', 'Camila', 'Fernanda', 'Isabella',
        'Laura', 'Beatriz', 'Carolina', 'Amanda', 'Patricia', 'Renata',
        'Tatiane', 'Sabrina', 'Vanessa', 'Leticia', 'Aline', 'Bianca',
        'Natalia', 'Daniela', 'Juliana', 'Mariana', 'Luana', 'Priscila', 'Elaine'
    ]

    sobrenomes = [
        'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira',
        'Alves', 'Pereira', 'Lima', 'Costa', 'Ribeiro', 'Martins',
        'Carvalho', 'Gomes', 'Mendes', 'Araujo', 'Rocha', 'Barbosa',
        'Teixeira', 'Pacheco', 'Nogueira', 'Farias', 'Moura',
        'Batista', 'Freitas'
    ]

    cursos_ifb = [
        'Tecnologia em Sistemas para Internet',
        'Tecnologia em Redes de Computadores',
        'Licenciatura em Matematica',
        'Tecnologia em Gestao Publica',
        'Tecnologia em Analise e Desenvolvimento de Sistemas',
        'Bacharelado em Ciencia da Computacao'
    ]

    alunos = []
    emails_utilizados = set()

    for aluno_id in range(1, 51):
        genero = random.choice(['M', 'F'])
        nome = random.choice(nomes_masculinos if genero == 'M' else nomes_femininos)
        sobrenome1 = random.choice(sobrenomes)
        sobrenome2 = random.choice(sobrenomes)
        nome_completo = f"{nome} {sobrenome1} {sobrenome2}"

        base_email = f"{nome.lower()}.{sobrenome1.lower()}"
        email = f"{base_email}@aluno.IFBpython.com"
        if email in emails_utilizados:
            email = f"{base_email}{aluno_id}@aluno.IFBpython.com"
        emails_utilizados.add(email)

        matricula = f"{random.choice([2022, 2023, 2024])}1{aluno_id:04d}"
        nascimento = date(2025 - random.randint(18, 30), random.randint(1, 12), random.randint(1, 28))

        aluno = Aluno.objects.create(
            nome=nome_completo,
            matricula=matricula,
            email=email,
            curso=random.choice(cursos_ifb),
            data_nascimento=nascimento,
            genero=genero
        )

        alunos.append(aluno)

    print(f"   Total: {len(alunos)} alunos criados")
    return alunos

def criar_turmas(professores, alunos):
    """Cria turmas e matriculas"""
    
    print("\nCriando turmas IFB...")
    
    turmas_dados = [
        {
            'nome': 'Programacao Python Avancada',
            'descricao': 'Introducao a estatistica para analise de dados',
            'professor': professores[0],
            'status': 'Ativa'
        },
        # ... outras turmas
    ]
    
    turma_objects = []
    alunos_alocados_como_representantes = set()  # <-- NOVO: controla representantes
    
    for dados in turmas_dados:
        turma = Turma.objects.create(
            nome=dados['nome'],
            descricao=dados['descricao'],
            professor=dados['professor'],
            data_inicio=date(2025, 2, 1),
            data_fim=date(2025, 12, 15),
            status=dados['status']
        )
        
        # Matricula 10-15 alunos aleatorios em cada turma
        alunos_turma = random.sample(alunos, random.randint(10, 15))
        for aluno in alunos_turma:
            Matricula.objects.create(
                turma=turma,
                aluno=aluno,
                data_matricula=date(2025, 2, 1),
                presenca_acumulada=random.randint(70, 95)
            )
        
        # Define um representante QUE AINDA NAO FOI REPRESENTANTE
        if alunos_turma:
            # Filtra alunos que ainda não são representantes
            alunos_disponiveis = [a for a in alunos_turma if a.id not in alunos_alocados_como_representantes]
            
            if alunos_disponiveis:
                representante = random.choice(alunos_disponiveis)
                turma.representante = representante
                turma.save()
                alunos_alocados_como_representantes.add(representante.id)
                print(f"   Representante: {representante.nome.split()[0]}")
            else:
                print(f"   AVISO: Nenhum aluno disponivel para ser representante")
        
        turma_objects.append(turma)
        print(f"   Turma criada: {dados['nome']}")
    
    return turma_objects

def criar_presencas_detalhadas(turmas):
    print("\nCriando presencas...")

    for turma in turmas:
        matriculas = Matricula.objects.filter(turma=turma)
        data_inicio = date(2025, 2, 10)

        for semana in range(16):
            data_aula = data_inicio + timedelta(weeks=semana)
            for matricula in matriculas:
                status = 'Presente' if random.random() < 0.9 else 'Ausente'
                Presenca.objects.create(
                    matricula=matricula,
                    data=data_aula,
                    status=status
                )


def criar_usuarios_adicionais():
    usuarios = [
        ('coordenador', 'coord123', 'Administradores'),
        ('prof.teste', 'prof123', 'Professores'),
        ('aluno.teste', 'aluno123', 'Alunos')
    ]

    for username, senha, grupo_nome in usuarios:
        user, _ = User.objects.get_or_create(username=username)
        user.set_password(senha)
        user.save()
        user.groups.add(Group.objects.get(name=grupo_nome))


def main():
    criar_grupos_permissoes()
    professores = criar_professores()
    alunos = criar_alunos()
    turmas = criar_turmas(professores, alunos)
    criar_presencas_detalhadas(turmas)
    criar_usuarios_adicionais()

    print("\nBANCO POPULADO COM SUCESSO")


if __name__ == '__main__':
    main()
