# Sistema de Chamada de Alunos – API REST

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15.2-red.svg)](https://www.django-rest-framework.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)]()

API RESTful para gerenciamento de chamada de alunos, integrada a **dashboards analíticos**, desenvolvida para a solução educacional **EduTrack Solutions**.

---

## 📌 Sumário
- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Scripts de Automação](#scripts-de-automação)
- [Uso com VSCode](#uso-com-vscode)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Modelo de Dados](#modelo-de-dados)
- [Autenticação](#autenticação)
- [Equipe](#equipe)
- [Licença](#licença)

---

## Visão Geral

Sistema backend desenvolvido para uma universidade pública com o objetivo de modernizar o processo de chamada de alunos, reduzindo o absenteísmo (estimado entre **20–30%**, conforme dados do INEP).

A API permite:
- Registro de presenças em tempo real
- Dashboards analíticos para gestão educacional
- Integração com sistemas de BI
- Controle de acesso por perfis (Administrador, Professor e Aluno)

---

## Funcionalidades

### Entidades Principais
- **Professores**: gestão de docentes e vínculo com turmas
- **Turmas**: disciplinas com períodos, status e professor responsável
- **Alunos**: dados cadastrais e informações para análises de equidade

### Relacionamentos
- **1:N** – Professor ↔ Turma
- **N:N** – Turma ↔ Aluno (tabela intermediária `Matricula`)
- **1:1** – Turma ↔ Aluno Representante

### Dashboard Analítico
- Estatísticas de presença por turma
- Indicadores de absenteísmo
- Relatórios por período e por curso

### Autenticação e Autorização
- Autenticação via **JWT**
- Perfis diferenciados (Administrador, Professor, Aluno)
- Permissões granulares por rota

---

## Tecnologias

### Backend
- Python **3.14+**
- Django **5.2**
- Django REST Framework **3.15.2**
- Django REST Framework Simple JWT **5.5.1**
- SQLite (ambiente de desenvolvimento)
- DRF Spectacular (Swagger / Redoc)

### Dependências completas

```txt
asgiref==3.11.0
attrs==25.4.0
Django==5.2
django-cors-headers==4.9.0
django-filter==24.3
djangorestframework==3.15.2
djangorestframework_simplejwt==5.5.1
drf-spectacular==0.29.0
inflection==0.5.1
jsonschema==4.25.1
jsonschema-specifications==2025.9.1
PyJWT==2.10.1
PyYAML==6.0.3
referencing==0.37.0
rpds-py==0.30.0
sqlparse==0.5.4
tzdata==2025.3
uritemplate==4.2.0
```

---

## Instalação

### Pré-requisitos
- Python 3.14 ou superior
- Git
- Virtualenv

### Passo a passo (Windows)

```bash
git clone <URL_DO_REPOSITORIO>
cd sistema-chamada-alunos
```

1. **Configurar o ambiente**
```bash
setup.bat
```

2. **Resetar o banco de dados**
```bash
reset_db.bat
```

3. **Popular dados de demonstração**
```bash
populate_demo.bat
```

4. **Iniciar o servidor**
```bash
run.bat
```

---

## Scripts de Automação

Os scripts `.bat` automatizam completamente o setup e execução do projeto.

### `setup.bat`
- Criação do ambiente virtual
- Instalação das dependências
- Validação do Django e DRF

### `reset_db.bat`
- Remove o banco SQLite existente
- Executa migrações
- Cria superusuário padrão

> ⚠️ **ATENÇÃO:** Este script apaga todos os dados existentes.

### `populate_demo.bat`
Popula o banco com dados realistas para demonstração:
- Professores com titulações
- 50 alunos distribuídos em cursos
- Turmas do curso de Desenvolvimento de Software BackEnd
- Presenças simuladas para 16 semanas
- Usuários de teste para todos os perfis
- Definição de representantes de turma

### `run.bat`
- Ativa o ambiente virtual
- Inicia o servidor Django na porta 8000
- Abre automaticamente o painel admin

---

## Uso com VSCode

### Extensões recomendadas
- Python (Microsoft)
- Django
- REST Client
- SQLite Viewer

### Execução via terminal integrado
```bash
.\setup.bat
.\run.bat
```

---

## Estrutura do Projeto

```text
API_CHAMADA_DE_ALUNOS/
├── src/
│   └── backend/
│       ├── app/
│       ├── core/
│       ├── scripts/
│       ├── manage.py
│       └── requirements.txt
├── populate_demo.bat
├── reset_db.bat
├── run.bat
├── setup.bat
└── .gitignore
```

---

## Modelo de Dados

A estrutura completa do banco de dados está documentada no arquivo: **[Database](explain_database.md)**

![Conceptual model - BRMW(corrigido)_page-0001](https://github.com/user-attachments/assets/af856fee-e18b-40fa-907e-e7079764bdb7)

---

## Autenticação

- Autenticação baseada em JWT
- Perfis suportados:
  - Administrador
  - Professor
  - Aluno

---

## Equipe

**Desenvolvimento:**
- Yuri Daquila – Backend Development
- Sóstenes H. – API Design & Documentation
- Sara Spinola – Database Modeling & Testing

**Instituição:** IFB Campus Estrutural  
**Curso:** Desenvolvimento de Software com Formação BackEnd – Python com Django  
**Professor:** Wellyelton Gualberto de Brito Rodrigues

---

## Licença

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

