# app/permissions.py (atualização)
from rest_framework import permissions
from .models import Turma, Matricula, Professor, Aluno

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsProfessorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        # Verifica se o usuário está associado a um professor
        return hasattr(request.user, 'professor')


class IsProfessorDaTurma(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if hasattr(request.user, 'professor'):
            if isinstance(obj, Turma):
                return obj.professor == request.user.professor
            elif hasattr(obj, 'turma'):
                return obj.turma.professor == request.user.professor
            elif hasattr(obj, 'matricula'):
                return obj.matricula.turma.professor == request.user.professor
        
        return False


class IsAlunoOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        if hasattr(request.user, 'aluno'):
            if isinstance(obj, Aluno):
                return obj == request.user.aluno
            elif hasattr(obj, 'aluno'):
                return obj.aluno == request.user.aluno
            elif hasattr(obj, 'matricula') and hasattr(obj.matricula, 'aluno'):
                return obj.matricula.aluno == request.user.aluno
        
        return False


class CanMarcarPresenca(permissions.BasePermission):
    """
    Permissão específica para marcar presenças.
    Apenas professores da turma ou administradores.
    """
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        if request.method == 'POST' and hasattr(request.user, 'professor'):
            # Verifica se o professor está tentando marcar presença em sua turma
            matricula_id = request.data.get('matricula')
            if matricula_id:
                try:
                    matricula = Matricula.objects.get(id=matricula_id)
                    return matricula.turma.professor == request.user.professor
                except Matricula.DoesNotExist:
                    return False
        
        return hasattr(request.user, 'professor')


class CanVerMinhasPresencas(permissions.BasePermission):
    """
    Permissão para alunos verem apenas suas próprias presenças.
    """
    def has_permission(self, request, view):
        if request.user.is_staff or hasattr(request.user, 'professor'):
            return True
        
        if hasattr(request.user, 'aluno'):
            # Alunos só podem ver suas próprias presenças
            if request.method == 'GET':
                return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or hasattr(request.user, 'professor'):
            return True
        
        if hasattr(request.user, 'aluno'):
            # Verifica se a presença pertence ao aluno
            return obj.matricula.aluno == request.user.aluno
        
        return False


class PublicReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class CoordenadorPermission(permissions.BasePermission):
    """
    Permissão para coordenadores (extensão do admin).
    Coordenadores podem criar/alunos/turmas, mas não deletar.
    """
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        if request.method == 'DELETE':
            return False  # Apenas admin pode deletar
        
        return request.user.is_authenticated and request.user.groups.filter(name='Coordenador').exists()