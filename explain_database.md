# Explain_DATABASE.md

## Projeto Integrador – Sistema de Chamada de Alunos

Este documento descreve **de forma completa e detalhada** a estrutura do banco de dados do projeto **Sistema de Chamada de Alunos**, servindo como referência técnica para desenvolvedores, avaliadores acadêmicos e auditores de sistemas educacionais.

O banco foi modelado para **suportar operações transacionais**, **consultas estatísticas**, **dashboards analíticos** e **integrações com sistemas de BI**, mantendo integridade relacional e escalabilidade.

---

## 1. Visão Geral da Arquitetura de Dados

- **SGBD utilizado no projeto**: SQLite (ambiente acadêmico e desenvolvimento)
- **SGBD recomendado para produção**: PostgreSQL
- **ORM**: Django ORM
- **Framework de API**: Django Rest Framework (DRF)
- **Autenticação**: JWT (djangorestframework-simplejwt)
- **Documentação de API**: drf-spectacular (Swagger / Redoc)
- **Padrão de modelagem**: Modelo Relacional Normalizado (3FN)

**Objetivos principais da camada de dados:**
- Controle transacional de presença
- Consultas estatísticas e agregações
- Dashboards educacionais
- Auditoria acadêmica

---

## 2. Entidades Principais

### 2.1 Professor

Representa os docentes responsáveis pelas turmas.

**Tabela:** `professor`

| Coluna | Tipo | Restrições | Descrição |
|------|------|------------|-----------|
| id | SERIAL | PK | Identificador único |
| nome | VARCHAR(150) | NOT NULL | Nome completo |
| email | VARCHAR(150) | UNIQUE, NOT NULL | Email institucional |
| departamento | VARCHAR(100) | NOT NULL | Departamento acadêmico |
| ativo | BOOLEAN | DEFAULT TRUE | Indica se está em exercício |
| data_cadastro | TIMESTAMP | DEFAULT NOW() | Data de cadastro |

**Observações:**
- Usado para métricas de carga docente
- Referenciado diretamente pela entidade Turma

---

### 2.2 Aluno

Representa os estudantes matriculados na instituição.

**Tabela:** `aluno`

| Coluna | Tipo | Restrições | Descrição |
|------|------|------------|-----------|
| id | SERIAL | PK | Identificador único |
| nome | VARCHAR(150) | NOT NULL | Nome completo |
| matricula | VARCHAR(50) | UNIQUE, NOT NULL | Número de matrícula |
| email | VARCHAR(150) | UNIQUE, NOT NULL | Email acadêmico |
| curso | VARCHAR(100) | NOT NULL | Curso de graduação |
| data_nascimento | DATE | NOT NULL | Data de nascimento |
| genero | VARCHAR(20) | NULL | Usado para análises estatísticas |

**Observações:**
- Permite análises de equidade e políticas públicas
- Relacionamento N:N com Turma

---

### 2.3 Turma

Representa disciplinas/turmas oferecidas pela universidade.

**Tabela:** `turma`

| Coluna | Tipo | Restrições | Descrição |
|------|------|------------|-----------|
| id | SERIAL | PK | Identificador único |
| nome | VARCHAR(150) | NOT NULL | Nome da disciplina |
| descricao | TEXT | NULL | Descrição da turma |
| professor_id | INTEGER | FK → professor(id) | Professor responsável |
| data_inicio | DATE | NOT NULL | Início da turma |
| data_fim | DATE | NOT NULL | Fim da turma |
| status | VARCHAR(20) | NOT NULL | Ativa / Concluída / Cancelada |
| representante_id | INTEGER | UNIQUE, FK → aluno(id) | Aluno representante |

**Observações:**
- Cada turma possui **um único professor**
- Cada turma pode ter **um único aluno representante**

---

## 3. Tabelas de Relacionamento

### 3.1 Matrícula (N:N – Turma ↔ Aluno)

Tabela intermediária que registra alunos matriculados em turmas.

**Tabela:** `matricula`

| Coluna | Tipo | Restrições | Descrição |
|------|------|------------|-----------|
| id | SERIAL | PK | Identificador único |
| aluno_id | INTEGER | FK → aluno(id) | Aluno matriculado |
| turma_id | INTEGER | FK → turma(id) | Turma |
| data_matricula | DATE | DEFAULT CURRENT_DATE | Data da matrícula |
| presenca_acumulada | DECIMAL(5,2) | DEFAULT 0 | % de presença |

**Restrições adicionais:**
- UNIQUE(aluno_id, turma_id)

**Uso estatístico:**
- Base para dashboards de frequência
- Indicadores de evasão

---

### 3.2 Presença

Registra cada chamada realizada em uma turma.

**Tabela:** `presenca`

| Coluna | Tipo | Restrições | Descrição |
|------|------|------------|-----------|
| id | SERIAL | PK | Identificador único |
| matricula_id | INTEGER | FK → matricula(id) | Relação aluno-turma |
| data | DATE | NOT NULL | Data da chamada |
| status | VARCHAR(20) | NOT NULL | Presente / Ausente / Justificado |

**Observações:**
- Permite cálculo de:
  - Média de presença por turma
  - Frequência individual
  - Estatísticas temporais

---

## 4. Estrutura Visual do Banco de Dados (Diagrama ASCII)

Abaixo está uma **representação visual textual** do modelo lógico do banco de dados. Esse diagrama facilita o entendimento rápido das entidades e relacionamentos, mesmo sem ferramentas gráficas.

```
┌──────────────┐        1        ┌──────────────┐
│  PROFESSOR   │────────────────▶│    TURMA     │
├──────────────┤      (1:N)     ├──────────────┤
│ id (PK)      │                │ id (PK)      │
│ nome         │                │ nome         │
│ email        │                │ descricao    │
│ departamento │                │ status       │
│ ativo        │                │ data_inicio  │
│ data_cadastro│                │ data_fim     │
└──────────────┘                │ professor_id │
                                │ representante_id (FK) │
                                └───────┬──────┘
                                        │
                                        │ 1:1
                                        ▼
                                ┌──────────────┐
                                │    ALUNO     │
                                ├──────────────┤
                                │ id (PK)      │
                                │ nome         │
                                │ matricula    │
                                │ email        │
                                │ curso        │
                                │ genero       │
                                └──────────────┘

                N:N (Matrícula)
┌──────────────┐   ◀────────────▶   ┌──────────────┐
│    ALUNO     │                    │    TURMA     │
└──────────────┘                    └──────────────┘
            │                              │
            │                              │
            ▼                              ▼
      ┌────────────────────────────────────────┐
      │              MATRICULA                 │
      ├────────────────────────────────────────┤
      │ id (PK)                                │
      │ aluno_id (FK)                          │
      │ turma_id (FK)                          │
      │ data_matricula                         │
      │ presenca_acumulada                     │
      └───────────────┬────────────────────────┘
                      │ 1:N
                      ▼
               ┌──────────────┐
               │   PRESENCA   │
               ├──────────────┤
               │ id (PK)      │
               │ matricula_id │
               │ data         │
               │ status       │
               └──────────────┘
```

**Legenda:**
- PK = Primary Key
- FK = Foreign Key
- 1:N = Um para muitos
- N:N = Muitos para muitos
- 1:1 = Um para um

---

## 4. Relacionamentos e Cardinalidade

| Relacionamento | Tipo | Descrição |
|--------------|------|-----------|
| Professor → Turma | 1:N | Um professor leciona várias turmas |
| Turma ↔ Aluno | N:N | Alunos podem cursar várias turmas |
| Turma → Representante | 1:1 | Uma turma possui um representante |
| Matrícula → Presença | 1:N | Uma matrícula possui várias presenças |

---

## 5. Integridade e Regras de Negócio

- Exclusão de professor **não remove turmas automaticamente** (RESTRICT)
- Exclusão de aluno **remove matrículas e presenças** (CASCADE)
- Apenas um representante por turma
- Um aluno não pode representar mais de uma turma

---

## 6. Suporte a Dashboards e BI

Consultas comuns suportadas:

- Taxa média de presença por turma
- Ranking de absenteísmo
- Frequência por período
- Carga docente por professor
- Comparativo entre cursos e gêneros

Exemplo de consulta:

```sql
SELECT t.nome, AVG(p.status = 'Presente') * 100 AS media_presenca
FROM presenca p
JOIN matricula m ON p.matricula_id = m.id
JOIN turma t ON m.turma_id = t.id
GROUP BY t.nome;
```

---

## 7. Segurança e Auditoria

- Dados sensíveis protegidos via autenticação JWT
- Separação clara entre dados públicos e privados
- Estrutura preparada para trilhas de auditoria

---

## 8. Dependências Utilizadas no Projeto

Abaixo estão listadas **todas as dependências efetivamente utilizadas** no desenvolvimento da API, garantindo reprodutibilidade do ambiente.

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

**Observações importantes:**
- O projeto utiliza **SQLite** como banco de dados, adequado para projetos acadêmicos e ambientes de desenvolvimento.
- A estrutura do banco foi projetada de forma **portável**, permitindo migração futura para PostgreSQL sem alterações estruturais.
- O uso de JWT garante separação clara de perfis (Administrador, Professor e Aluno).

---

## 9. Considerações Finais

A estrutura de banco de dados e o conjunto de dependências adotados neste projeto foram escolhidos para:

- Atender integralmente os requisitos do Projeto Integrador
- Facilitar testes e avaliação acadêmica
- Manter simplicidade de setup (SQLite)
- Permitir escalabilidade futura (PostgreSQL)
- Garantir segurança, rastreabilidade e clareza de dados

Esta documentação complementa o código-fonte e serve como referência oficial para manutenção, auditoria e evolução do sistema.

---

**Autor:** Projeto Integrador – Sistema de Chamada de Alunos  
**Stack:** Django 5.2 • DRF • JWT • SQLite  
**Finalidade:** Documentação técnica para GitHub

