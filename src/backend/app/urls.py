# app/urls.py - VERSÃO SIMPLIFICADA
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_auth

router = DefaultRouter()
router.register(r'professores', views.ProfessorViewSet, basename='professor')
router.register(r'alunos', views.AlunoViewSet, basename='aluno')
router.register(r'turmas', views.TurmaViewSet, basename='turma')
router.register(r'matriculas', views.MatriculaViewSet, basename='matricula')
router.register(r'presencas', views.PresencaViewSet, basename='presenca')

# URLs de autenticação
auth_urlpatterns = [
    path('registro/', views_auth.RegisterView.as_view(), name='registro'),
    path('login/', views_auth.LoginView.as_view(), name='login'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),
    path('meu-perfil/', views_auth.UserProfileView.as_view(), name='meu-perfil'),
    path('alterar-senha/', views_auth.ChangePasswordView.as_view(), name='alterar-senha'),
    path('recuperar-senha/', views_auth.ResetPasswordView.as_view(), name='recuperar-senha'),
    path('recuperar-senha/confirmar/', views_auth.ResetPasswordConfirmView.as_view(), name='recuperar-senha-confirmar'),
]

# URLs principais
urlpatterns = [
    # API Router (principal)
    path('', include(router.urls)),
    
    # Autenticação
    path('auth/', include(auth_urlpatterns)),
    
    # Views específicas
    path('minhas-turmas/', views.MinhasTurmasView.as_view(), name='minhas-turmas'),
    path('turmas-ativas/', views.TurmasAtivasView.as_view(), name='turmas-ativas'),
    path('professores-publicos/', views.ProfessoresPublicosView.as_view(), name='professores-publicos'),
]