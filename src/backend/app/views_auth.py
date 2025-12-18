# app/views_auth.py - VERSÃO SIMPLIFICADA
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.contrib.auth import logout

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, ResetPasswordSerializer,
    ResetPasswordConfirmSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tipo_usuario = request.data.get('tipo_usuario', 'aluno')
        user = serializer.save()
        user._tipo_usuario_registro = tipo_usuario
        user.save()
        
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context=self.get_serializer_context()).data
        
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Usuário registrado com sucesso.'
        }, status=status.HTTP_201_CREATED)

class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context={'request': request}).data
        
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Login realizado com sucesso.'
        })

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({
            'message': 'Logout realizado com sucesso.'
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Senha alterada com sucesso.',
            'token': new_token.key
        }, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Em produção, enviaria email real
        return Response({
            'message': 'Email de recuperação enviado com sucesso.'
        }, status=status.HTTP_200_OK)

class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'message': 'Senha redefinida com sucesso. Faça login com a nova senha.'
        }, status=status.HTTP_200_OK)