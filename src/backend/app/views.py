# app/views.py - VERSÃO LIMPA E FUNCIONAL
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from .models import Professor, Aluno, Turma, Matricula, Presenca
from .serializers import (
    ProfessorSerializer, AlunoSerializer, TurmaSerializer,
    MatriculaSerializer, PresencaSerializer, DashboardTurmaSerializer,
    ProfessorTurmasSerializer, TurmaAlunosSerializer, RepresentanteSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsProfessorOrAdmin, IsProfessorDaTurma,
    IsAlunoOrReadOnly, PublicReadOnly
)


# ========== VIEWSETS PRINCIPAIS ==========

class ProfessorViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar professores"""
    queryset = Professor.objects.all().order_by('nome')
    serializer_class = ProfessorSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ativo', 'departamento']
    search_fields = ['nome', 'email', 'departamento']


class AlunoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar alunos"""
    queryset = Aluno.objects.all().order_by('nome')
    serializer_class = AlunoSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['curso', 'genero']
    search_fields = ['nome', 'matricula', 'email', 'curso']


class TurmaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar turmas"""
    queryset = Turma.objects.all().order_by('-data_inicio', 'nome')
    serializer_class = TurmaSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'professor']
    search_fields = ['nome', 'descricao']
    
    def get_queryset(self):
        """Filtra turmas para professores verem apenas suas turmas"""
        queryset = super().get_queryset()
        
        # Se o usuário é um professor (não admin), mostra apenas suas turmas
        user = self.request.user
        if user.is_authenticated and not user.is_staff and hasattr(user, 'professor'):
            return queryset.filter(professor=user.professor)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def atribuir_professor(self, request, pk=None):
        """Atribui professor a turma"""
        turma = self.get_object()
        professor_id = request.data.get('professor_id')
        
        if not professor_id:
            return Response(
                {"error": "professor_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            professor = Professor.objects.get(id=professor_id)
        except Professor.DoesNotExist:
            return Response(
                {"error": "Professor não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        turma.professor = professor
        turma.save()
        
        serializer = self.get_serializer(turma)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def matricular_aluno(self, request, pk=None):
        """Matricula aluno na turma"""
        turma = self.get_object()
        aluno_id = request.data.get('aluno_id')
        
        if not aluno_id:
            return Response(
                {"error": "aluno_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            aluno = Aluno.objects.get(id=aluno_id)
        except Aluno.DoesNotExist:
            return Response(
                {"error": "Aluno não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verifica se o aluno já está matriculado
        if Matricula.objects.filter(turma=turma, aluno=aluno).exists():
            return Response(
                {"error": "Aluno já matriculado nesta turma"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        matricula = Matricula.objects.create(turma=turma, aluno=aluno)
        serializer = MatriculaSerializer(matricula)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser])
    def definir_representante(self, request, pk=None):
        """Define aluno como representante da turma"""
        turma = self.get_object()
        aluno_id = request.data.get('aluno_id')
        
        if aluno_id is None:
            # Remove o representante
            turma.representante = None
            turma.save()
            return Response(
                {"message": "Representante removido com sucesso"},
                status=status.HTTP_200_OK
            )
        
        try:
            aluno = Aluno.objects.get(id=aluno_id)
        except Aluno.DoesNotExist:
            return Response(
                {"error": "Aluno não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verifica se o aluno está matriculado na turma
        if not Matricula.objects.filter(turma=turma, aluno=aluno).exists():
            return Response(
                {"error": "Aluno não está matriculado nesta turma"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        turma.representante = aluno
        turma.save()
        
        serializer = self.get_serializer(turma)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def alunos(self, request, pk=None):
        """Lista alunos matriculados na turma"""
        turma = self.get_object()
        matriculas = Matricula.objects.filter(turma=turma)
        serializer = MatriculaSerializer(matriculas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def representante(self, request, pk=None):
        """Retorna o representante da turma"""
        turma = self.get_object()
        if turma.representante:
            serializer = AlunoSerializer(turma.representante)
            return Response(serializer.data)
        return Response({"message": "Nenhum representante definido"})
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Retorna dashboard da turma"""
        turma = self.get_object()
        
        # Calcula estatísticas
        matriculas = Matricula.objects.filter(turma=turma)
        total_presencas = Presenca.objects.filter(matricula__turma=turma).count()
        
        if matriculas.exists():
            media_presenca = matriculas.aggregate(media=Avg('presenca_acumulada'))['media']
        else:
            media_presenca = 0
        
        data = {
            'turma': turma,
            'total_presencas': total_presencas,
            'media_presenca': round(media_presenca, 2) if media_presenca else 0,
        }
        
        serializer = DashboardTurmaSerializer(data)
        return Response(serializer.data)


class MatriculaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar matrículas"""
    queryset = Matricula.objects.all().order_by('-data_matricula')
    serializer_class = MatriculaSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['turma']
    search_fields = [
        'aluno__nome', 'aluno__matricula',
        'turma__nome'
    ]


class PresencaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar presenças"""
    queryset = Presenca.objects.all().order_by('-data', '-data_registro')
    serializer_class = PresencaSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'data', 'matricula__turma']
    search_fields = [
        'matricula__aluno__nome',
        'matricula__aluno__matricula',
        'observacao'
    ]
    
    def get_queryset(self):
        """Filtra o queryset baseado no tipo de usuário"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_staff:
            return queryset  # Admin vê tudo
        
        if hasattr(user, 'professor'):
            # Professor vê apenas presenças de suas turmas
            return queryset.filter(matricula__turma__professor=user.professor)
        
        if hasattr(user, 'aluno'):
            # Aluno vê apenas suas próprias presenças
            return queryset.filter(matricula__aluno=user.aluno)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Verifica se o professor pode marcar presença nesta matrícula"""
        matricula = serializer.validated_data['matricula']
        
        if self.request.user.is_staff:
            serializer.save()
            return
        
        if hasattr(self.request.user, 'professor'):
            if matricula.turma.professor == self.request.user.professor:
                serializer.save()
            else:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Você não pode marcar presença nesta turma")


# ========== VIEWS PÚBLICAS ==========

class TurmasAtivasView(generics.ListAPIView):
    """
    GET /api/turmas-ativas/
    Lista pública de turmas ativas (sem dados pessoais)
    """
    queryset = Turma.objects.filter(status='Ativa').order_by('-data_inicio')
    serializer_class = TurmaSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['public_view'] = True
        return context


class ProfessoresPublicosView(generics.ListAPIView):
    """
    GET /api/professores-publicos/
    Lista pública de professores (apenas nomes e departamentos)
    """
    queryset = Professor.objects.filter(ativo=True).order_by('nome')
    serializer_class = ProfessorSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['public_view'] = True
        return context


# ========== VIEWS DO SISTEMA ==========

class MinhasTurmasView(generics.ListAPIView):
    """
    GET /api/minhas-turmas/
    Retorna as turmas do professor logado
    """
    serializer_class = TurmaSerializer
    permission_classes = [IsProfessorOrAdmin]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'professor'):
            return Turma.objects.filter(professor=self.request.user.professor)
        return Turma.objects.none()