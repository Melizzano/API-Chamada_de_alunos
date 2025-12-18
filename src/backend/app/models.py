# app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Professor(models.Model):
    """Entidade A: Representa os docentes responsáveis por turmas"""
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    departamento = models.CharField(max_length=100, verbose_name="Departamento")
    ativo = models.BooleanField(default=True, verbose_name="Em Exercício")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='professor',
        null=True,
        blank=True,
        verbose_name="Usuário do Sistema"
    )

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.departamento}"
    
    @property
    def quantidade_turmas(self):
        return self.turmas.count()


class Aluno(models.Model):
    """Entidade C: Representa os estudantes matriculados"""
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='aluno',
        null=True,
        blank=True,
        verbose_name="Usuário do Sistema"
    )    
    
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    curso = models.CharField(max_length=100, verbose_name="Curso")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    genero = models.CharField(
        max_length=1, 
        choices=GENERO_CHOICES, 
        verbose_name="Gênero"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.matricula}) - {self.curso}"
    
    @property
    def idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class Turma(models.Model):
    """Entidade B: Representa as classes ou disciplinas lecionadas"""
    STATUS_CHOICES = [
        ('Ativa', 'Ativa'),
        ('Concluída', 'Concluída'),
        ('Cancelada', 'Cancelada'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome da Turma")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    professor = models.ForeignKey(
        Professor, 
        on_delete=models.PROTECT,
        related_name='turmas',
        verbose_name="Professor Responsável"
    )
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Ativa',
        verbose_name="Status"
    )
    representante = models.OneToOneField(
        Aluno,
        on_delete=models.SET_NULL,
        related_name='turma_representante',
        null=True,
        blank=True,
        verbose_name="Aluno Representante"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ['-data_inicio', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.professor.nome} ({self.status})"
    
    @property
    def duracao_dias(self):
        return (self.data_fim - self.data_inicio).days
    
    @property
    def total_alunos(self):
        return self.matriculas.count()


class Matricula(models.Model):
    """Tabela de junção para relacionamento N:N entre Turma e Aluno"""
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name="Aluno"
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name="Turma"
    )
    data_matricula = models.DateTimeField(auto_now_add=True, verbose_name="Data da Matrícula")
    presenca_acumulada = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Presença Acumulada (%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = ['aluno', 'turma']
        ordering = ['-data_matricula']
    
    def __str__(self):
        return f"{self.aluno.nome} em {self.turma.nome}"
    
    def calcular_presenca_acumulada(self):
        """Calcula a porcentagem de presença do aluno na turma"""
        total_aulas = self.presencas.count()
        if total_aulas == 0:
            return 0
        
        presentes = self.presencas.filter(status='Presente').count()
        return round((presentes / total_aulas) * 100, 2)


class Presenca(models.Model):
    """Entidade para registrar as presenças dos alunos"""
    STATUS_CHOICES = [
        ('Presente', 'Presente'),
        ('Ausente', 'Ausente'),
        ('Justificado', 'Justificado'),
    ]
    
    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='presencas',
        verbose_name="Matrícula"
    )
    data = models.DateField(verbose_name="Data da Aula")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Presente',
        verbose_name="Status"
    )
    observacao = models.TextField(blank=True, verbose_name="Observação")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    
    class Meta:
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"
        unique_together = ['matricula', 'data']
        ordering = ['-data', 'matricula__aluno__nome']
    
    def __str__(self):
        return f"{self.matricula.aluno.nome} - {self.data} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Atualiza a presença acumulada ao salvar"""
        super().save(*args, **kwargs)
        self.matricula.presenca_acumulada = self.matricula.calcular_presenca_acumulada()
        self.matricula.save()