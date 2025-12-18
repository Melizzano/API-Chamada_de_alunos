# src/backend/app/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .models import Professor, Aluno

# ============================================================================
# 1. SIGNALS PARA USER (Quando usuário é criado/atualizado)
# ============================================================================

@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Signal para criar perfil automaticamente quando um usuário é criado.
    Respeita o tipo_usuario passado durante o registro.
    """
    if created:
        print(f"[SIGNAL] Criando perfil para usuário: {instance.username}")
        
        # Verifica se já tem perfil (para evitar duplicação)
        tem_professor = hasattr(instance, 'professor')
        tem_aluno = hasattr(instance, 'aluno')
        
        if tem_professor or tem_aluno:
            print(f"[SIGNAL] Usuário já tem perfil: {tem_professor and 'Professor' or tem_aluno and 'Aluno'}")
            return
        
        # Tenta obter o tipo_usuario do contexto (passado pela view de registro)
        tipo_usuario = getattr(instance, '_tipo_usuario_registro', None)
        
        print(f"[SIGNAL] Tipo de usuário detectado: {tipo_usuario or 'Não especificado'}")
        
        if tipo_usuario == 'professor':
            criar_perfil_professor(instance)
        else:
            # Padrão é aluno (para compatibilidade com criações manuais)
            criar_perfil_aluno(instance)
        
        # Limpa o atributo temporário
        if hasattr(instance, '_tipo_usuario_registro'):
            delattr(instance, '_tipo_usuario_registro')

# ============================================================================
# 2. FUNÇÕES AUXILIARES PARA CRIAR PERFIS
# ============================================================================

def criar_perfil_professor(usuario):
    """Cria perfil de professor para o usuário"""
    try:
        # Verifica se já existe professor com este email
        professor_existente = Professor.objects.filter(email=usuario.email).first()
        
        if professor_existente:
            # Se já existe, associa ao usuário
            professor_existente.usuario = usuario
            professor_existente.save()
            print(f"[SIGNAL] Professor existente associado: {professor_existente.nome}")
        else:
            # Cria novo professor
            professor = Professor.objects.create(
                usuario=usuario,
                nome=usuario.get_full_name() or usuario.username,
                email=usuario.email,
                departamento='A definir',
                ativo=True
            )
            print(f"[SIGNAL] Novo professor criado: {professor.nome}")
        
        # Sincroniza grupos
        sincronizar_grupos_professor(usuario)
            
        print(f"[SIGNAL] Usuário {usuario.username} agora é Professor")
        
    except Exception as e:
        print(f"[SIGNAL] Erro ao criar perfil de professor: {e}")
        # Fallback: cria perfil de aluno em caso de erro
        criar_perfil_aluno(usuario)

def criar_perfil_aluno(usuario):
    """Cria perfil de aluno para o usuário"""
    try:
        # Verifica se já existe aluno com este email
        aluno_existente = Aluno.objects.filter(email=usuario.email).first()
        
        if aluno_existente:
            # Se já existe, associa ao usuário
            aluno_existente.usuario = usuario
            aluno_existente.save()
            print(f"[SIGNAL] Aluno existente associado: {aluno_existente.nome}")
        else:
            # Cria novo aluno
            aluno = Aluno.objects.create(
                usuario=usuario,
                nome=usuario.get_full_name() or usuario.username,
                email=usuario.email,
                matricula=f"MAT{usuario.id:06d}",
                curso='A definir',
                data_nascimento='2000-01-01',
                genero='N'
            )
            print(f"[SIGNAL] Novo aluno criado: {aluno.nome}")
        
        # Sincroniza grupos
        sincronizar_grupos_aluno(usuario)
            
        print(f"[SIGNAL] Usuário {usuario.username} agora é Aluno")
        
    except Exception as e:
        print(f"[SIGNAL] Erro ao criar perfil de aluno: {e}")

# ============================================================================
# 3. SIGNALS PARA PROFESSOR (Quando professor é criado/atualizado)
# ============================================================================

@receiver(post_save, sender=Professor)
def criar_usuario_para_professor(sender, instance, created, **kwargs):
    """
    Cria um usuário automaticamente quando um professor é criado sem usuário
    (Via Django Admin ou API)
    """
    if created and not instance.usuario:
        print(f"[SIGNAL-PROFESSOR] Criando usuário para professor: {instance.nome}")
        
        try:
            # Cria username baseado no email
            username_base = instance.email.split('@')[0]
            username = username_base
            
            # Garante username único
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            
            # Cria o usuário
            user = User.objects.create_user(
                username=username,
                email=instance.email,
                password='senha123',  # Senha padrão
                first_name=instance.nome.split()[0] if ' ' in instance.nome else '',
                last_name=' '.join(instance.nome.split()[1:]) if ' ' in instance.nome else '',
                is_staff=False  # Professores NÃO têm acesso ao admin por padrão
            )
            
            # Associa o usuário ao professor
            instance.usuario = user
            
            # Usamos update para evitar recursão do signal
            Professor.objects.filter(id=instance.id).update(usuario=user)
            
            print(f"[SIGNAL-PROFESSOR] Usuário criado: {username} para professor {instance.nome}")
            
            # Agora sincroniza os grupos (após associar o usuário)
            sincronizar_grupos_professor(user)
            
        except Exception as e:
            print(f"[SIGNAL-PROFESSOR] Erro ao criar usuário para professor: {e}")

@receiver(post_save, sender=Professor)
def atualizar_usuario_professor(sender, instance, created, **kwargs):
    """
    Atualiza grupos do usuário quando um professor é atualizado
    """
    if instance.usuario and not created:  # Apenas para updates, não criação
        try:
            sincronizar_grupos_professor(instance.usuario)
            print(f"[SIGNAL-PROFESSOR] Usuário {instance.usuario.username} sincronizado como Professor")
        except Exception as e:
            print(f"[SIGNAL-PROFESSOR] Erro ao sincronizar grupos: {e}")

# ============================================================================
# 4. SIGNALS PARA ALUNO (Quando aluno é criado/atualizado)
# ============================================================================

@receiver(post_save, sender=Aluno)
def criar_usuario_para_aluno(sender, instance, created, **kwargs):
    """
    Cria um usuário automaticamente quando um aluno é criado sem usuário
    """
    if created and not instance.usuario:
        print(f"[SIGNAL-ALUNO] Criando usuário para aluno: {instance.nome}")
        
        try:
            # Cria username baseado no email ou matrícula
            username_base = instance.email.split('@')[0] if instance.email else instance.matricula.lower()
            username = username_base
            
            # Garante username único
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            
            # Cria o usuário
            user = User.objects.create_user(
                username=username,
                email=instance.email,
                password='senha123',  # Senha padrão
                first_name=instance.nome.split()[0] if ' ' in instance.nome else '',
                last_name=' '.join(instance.nome.split()[1:]) if ' ' in instance.nome else '',
                is_staff=False  # Alunos não têm acesso ao admin
            )
            
            # Associa o usuário ao aluno
            instance.usuario = user
            Aluno.objects.filter(id=instance.id).update(usuario=user)
            
            print(f"[SIGNAL-ALUNO] Usuário criado: {username} para aluno {instance.nome}")
            
            # Sincroniza grupos
            sincronizar_grupos_aluno(user)
            
        except Exception as e:
            print(f"[SIGNAL-ALUNO] Erro ao criar usuário para aluno: {e}")

@receiver(post_save, sender=Aluno)
def atualizar_usuario_aluno(sender, instance, created, **kwargs):
    """
    Atualiza grupos do usuário quando um aluno é atualizado
    """
    if instance.usuario and not created:
        try:
            sincronizar_grupos_aluno(instance.usuario)
            print(f"[SIGNAL-ALUNO] Usuário {instance.usuario.username} sincronizado como Aluno")
        except Exception as e:
            print(f"[SIGNAL-ALUNO] Erro ao sincronizar grupos: {e}")

# ============================================================================
# 5. FUNÇÕES DE SINCRONIZAÇÃO DE GRUPOS
# ============================================================================

def sincronizar_grupos_professor(usuario):
    """Sincroniza grupos para um usuário professor"""
    # Adiciona ao grupo Professor
    grupo_professor, _ = Group.objects.get_or_create(name='Professor')
    usuario.groups.add(grupo_professor)
    
    # Remove do grupo Aluno se estiver
    grupo_aluno = Group.objects.filter(name='Aluno').first()
    if grupo_aluno and grupo_aluno in usuario.groups.all():
        usuario.groups.remove(grupo_aluno)
    
    # Atualiza email se necessário
    if hasattr(usuario, 'professor') and usuario.professor.email != usuario.email:
        usuario.email = usuario.professor.email
        usuario.save()

def sincronizar_grupos_aluno(usuario):
    """Sincroniza grupos para um usuário aluno"""
    # Adiciona ao grupo Aluno
    grupo_aluno, _ = Group.objects.get_or_create(name='Aluno')
    usuario.groups.add(grupo_aluno)
    
    # Remove do grupo Professor se estiver
    grupo_professor = Group.objects.filter(name='Professor').first()
    if grupo_professor and grupo_professor in usuario.groups.all():
        usuario.groups.remove(grupo_professor)
    
    # Atualiza email se necessário
    if hasattr(usuario, 'aluno') and usuario.aluno.email != usuario.email:
        usuario.email = usuario.aluno.email
        usuario.save()

# ============================================================================
# 6. SIGNAL AUXILIAR (pre_save para capturar tipo_usuario)
# ============================================================================

@receiver(pre_save, sender=User)
def capturar_tipo_usuario(sender, instance, **kwargs):
    """
    Captura o tipo_usuario antes de salvar o usuário.
    Isso permite que o Signal post_save saiba qual perfil criar.
    """
    # Só processa se for uma nova instância (id é None)
    if not instance.pk:
        # O tipo_usuario é armazenado como atributo temporário
        if hasattr(instance, '_tipo_usuario_registro'):
            print(f"[PRE-SIGNAL] Tipo de usuário capturado: {instance._tipo_usuario_registro}")