# app/admin.py - VERSÃO SEM ERROS
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Professor, Aluno, Turma, Matricula, Presenca

# ========== ADMIN CUSTOMIZADO PARA USER ==========

# Verificar se User já está registrado e desregistrar
if admin.site.is_registered(User):
    admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Em vez de adicionar um novo fieldset, vamos modificar um existente
    # ou adicionar apenas se não existir
    def get_fieldsets(self, request, obj=None):
        """Modifica os fieldsets para incluir grupos"""
        fieldsets = super().get_fieldsets(request, obj)
        
        # Adiciona grupos ao fieldset de permissões se ele existir
        for i, (title, fields) in enumerate(fieldsets):
            if 'groups' in fields.get('fields', []):
                # Já tem grupos, não faz nada
                return fieldsets
            
            # Verifica se é o fieldset de permissões
            if title == 'Permissions' or 'user_permissions' in fields.get('fields', []):
                # Adiciona groups ao fieldset de permissões
                if 'fields' in fields:
                    fields['fields'] = fields['fields'] + ('groups',)
                return fieldsets
        
        # Se não encontrou fieldset de permissões, adiciona um novo
        fieldsets = fieldsets + (
            ('Grupos', {
                'fields': ('groups',),
            }),
        )
        
        return fieldsets
    
    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Grupos'
    
    # Adicionar ações customizadas
    actions = ['make_staff', 'make_not_staff']
    
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)
    make_staff.short_description = "Tornar selecionados como staff (acesso admin)"
    
    def make_not_staff(self, request, queryset):
        queryset.update(is_staff=False)
    make_not_staff.short_description = "Remover status staff dos selecionados"

# Registrar o User customizado
admin.site.register(User, CustomUserAdmin)

# ========== ADMINS PARA OS MODELOS DO APP ==========

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'departamento', 'ativo', 'quantidade_turmas', 'data_cadastro')
    list_filter = ('ativo', 'departamento', 'data_cadastro')
    search_fields = ('nome', 'email', 'departamento')
    ordering = ('nome',)
    readonly_fields = ('data_cadastro',)

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'email', 'curso', 'idade', 'genero', 'data_cadastro')
    list_filter = ('curso', 'genero', 'data_cadastro')
    search_fields = ('nome', 'matricula', 'email', 'curso')
    ordering = ('nome',)
    readonly_fields = ('data_cadastro',)

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'professor', 'status', 'data_inicio', 'data_fim', 'total_alunos', 'representante')
    list_filter = ('status', 'data_inicio', 'data_fim', 'professor')
    search_fields = ('nome', 'descricao', 'professor__nome')
    ordering = ('-data_inicio', 'nome')
    readonly_fields = ('data_cadastro',)
    autocomplete_fields = ('professor', 'representante')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_matricula', 'presenca_acumulada')
    list_filter = ('turma', 'data_matricula')
    search_fields = ('aluno__nome', 'aluno__matricula', 'turma__nome')
    ordering = ('-data_matricula',)
    readonly_fields = ('data_matricula',)
    autocomplete_fields = ('aluno', 'turma')

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('aluno_nome', 'turma_nome', 'data', 'status', 'data_registro')
    list_filter = ('status', 'data', 'matricula__turma')
    search_fields = ('matricula__aluno__nome', 'matricula__aluno__matricula', 'observacao')
    ordering = ('-data', '-data_registro')
    readonly_fields = ('data_registro',)
    
    def aluno_nome(self, obj):
        return obj.matricula.aluno.nome
    aluno_nome.short_description = 'Aluno'
    
    def turma_nome(self, obj):
        return obj.matricula.turma.nome
    turma_nome.short_description = 'Turma'