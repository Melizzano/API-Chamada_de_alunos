# app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from .models import Professor, Aluno, Turma, Matricula, Presenca
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_field


class ProfessorSerializer(serializers.ModelSerializer):
    quantidade_turmas = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Professor
        fields = [
            'id', 'nome', 'email', 'departamento', 
            'ativo', 'data_cadastro', 'quantidade_turmas'
        ]
        read_only_fields = ['id', 'data_cadastro']
    
    def to_representation(self, instance):
        """Personaliza a representação para views públicas"""
        representation = super().to_representation(instance)
        context = self.context
        
        # Se for uma view pública, remove dados sensíveis
        if context.get('public_view', False):
            fields_to_keep = ['id', 'nome', 'departamento', 'ativo']
            return {k: v for k, v in representation.items() if k in fields_to_keep}
        
        return representation


class AlunoSerializer(serializers.ModelSerializer):
    idade = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Aluno
        fields = [
            'id', 'nome', 'matricula', 'email', 'curso',
            'data_nascimento', 'genero', 'data_cadastro', 'idade'
        ]
        read_only_fields = ['id', 'data_cadastro']
    
    def validate_matricula(self, value):
        """Valida se a matrícula já existe"""
        if self.instance and self.instance.matricula == value:
            return value
        
        if Aluno.objects.filter(matricula=value).exists():
            raise serializers.ValidationError("Matrícula já cadastrada")
        return value


class TurmaSerializer(serializers.ModelSerializer):
    professor_nome = serializers.CharField(source='professor.nome', read_only=True)
    total_alunos = serializers.IntegerField(read_only=True)
    duracao_dias = serializers.IntegerField(read_only=True)
    representante_nome = serializers.CharField(source='representante.nome', read_only=True, allow_null=True)
    
    class Meta:
        model = Turma
        fields = [
            'id', 'nome', 'descricao', 'professor', 'professor_nome',
            'data_inicio', 'data_fim', 'status', 'representante',
            'representante_nome', 'data_cadastro', 'total_alunos', 'duracao_dias'
        ]
        read_only_fields = ['id', 'data_cadastro']
    
    def validate(self, data):
        """Valida se data_inicio é anterior a data_fim"""
        if 'data_inicio' in data and 'data_fim' in data:
            if data['data_inicio'] >= data['data_fim']:
                raise serializers.ValidationError({
                    "data_fim": "Data de término deve ser posterior à data de início"
                })
        return data
    
    def to_representation(self, instance):
        """Personaliza a representação para views públicas"""
        representation = super().to_representation(instance)
        context = self.context
        
        # Se for uma view pública, remove dados sensíveis
        if context.get('public_view', False):
            fields_to_keep = [
                'id', 'nome', 'descricao', 'professor_nome',
                'data_inicio', 'data_fim', 'status', 'total_alunos', 'duracao_dias'
            ]
            return {k: v for k, v in representation.items() if k in fields_to_keep}
        
        return representation


class MatriculaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    turma_nome = serializers.CharField(source='turma.nome', read_only=True)
    aluno_matricula = serializers.CharField(source='aluno.matricula', read_only=True)
    
    class Meta:
        model = Matricula
        fields = [
            'id', 'aluno', 'aluno_nome', 'aluno_matricula',
            'turma', 'turma_nome', 'data_matricula', 'presenca_acumulada'
        ]
        read_only_fields = ['id', 'data_matricula', 'presenca_acumulada']


class PresencaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='matricula.aluno.nome', read_only=True)
    turma_nome = serializers.CharField(source='matricula.turma.nome', read_only=True)
    aluno_matricula = serializers.CharField(source='matricula.aluno.matricula', read_only=True)
    
    class Meta:
        model = Presenca
        fields = [
            'id', 'matricula', 'aluno_nome', 'aluno_matricula',
            'turma_nome', 'data', 'status', 'observacao', 'data_registro'
        ]
        read_only_fields = ['id', 'data_registro']


class DashboardTurmaSerializer(serializers.Serializer):
    """Serializer para a rota de dashboard da turma"""
    turma = serializers.SerializerMethodField()
    professor = serializers.SerializerMethodField()
    alunos_matriculados = serializers.SerializerMethodField()
    total_presencas = serializers.IntegerField(read_only=True)
    media_presenca = serializers.FloatField(read_only=True)
    representante = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.DictField(child=serializers.CharField()))
    def get_turma(self, obj):
        turma_data = {
            'id': obj['turma'].id,
            'nome': obj['turma'].nome,
            'descricao': obj['turma'].descricao,
            'data_inicio': obj['turma'].data_inicio,
            'data_fim': obj['turma'].data_fim,
            'status': obj['turma'].status,
            'total_alunos': obj['turma'].total_alunos,
            'duracao_dias': obj['turma'].duracao_dias
        }
        return turma_data
    
    @extend_schema_field(serializers.DictField(child=serializers.CharField()))
    def get_professor(self, obj):
        professor = obj['turma'].professor
        return {
            'id': professor.id,
            'nome': professor.nome,
            'departamento': professor.departamento
        }
    
    @extend_schema_field(serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    ))
    def get_alunos_matriculados(self, obj):
        matriculas = Matricula.objects.filter(turma=obj['turma']).select_related('aluno')
        data = []
        for matricula in matriculas:
            data.append({
                'id': matricula.id,
                'aluno': {
                    'id': matricula.aluno.id,
                    'nome': matricula.aluno.nome,
                    'matricula': matricula.aluno.matricula
                },
                'presenca_acumulada': matricula.presenca_acumulada,
                'data_matricula': matricula.data_matricula
            })
        return data
    
    @extend_schema_field(serializers.DictField(
        child=serializers.CharField(), 
        allow_null=True
    ))
    def get_representante(self, obj):
        representante = obj['turma'].representante
        if representante:
            return {
                'id': representante.id,
                'nome': representante.nome,
                'matricula': representante.matricula
            }
        return None

# Serializers para rotas específicas
class ProfessorTurmasSerializer(serializers.ModelSerializer):
    turmas = TurmaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Professor
        fields = ['id', 'nome', 'turmas']


class TurmaAlunosSerializer(serializers.ModelSerializer):
    alunos = serializers.SerializerMethodField()
    
    class Meta:
        model = Turma
        fields = ['id', 'nome', 'alunos']
    
    @extend_schema_field(serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    ))
    def get_alunos(self, obj):
        matriculas = Matricula.objects.filter(turma=obj).select_related('aluno')
        return MatriculaSerializer(matriculas, many=True).data


class RepresentanteSerializer(serializers.ModelSerializer):
    representante = AlunoSerializer(read_only=True)
    
    class Meta:
        model = Turma
        fields = ['id', 'nome', 'representante']


class UserSerializer(serializers.ModelSerializer):
    grupo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'grupo']
        read_only_fields = ['id', 'grupo']
    
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_grupo(self, obj):
        if obj.is_staff:
            return 'Administrador'
        
        grupos = obj.groups.all()
        if grupos.exists():
            return grupos.first().name
        return 'Sem grupo'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    tipo_usuario = serializers.ChoiceField(
        choices=[('aluno', 'Aluno'), ('professor', 'Professor')],
        required=False,
        default='aluno',
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'tipo_usuario')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        # Validação existente...
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs
    
    def create(self, validated_data):
        # Remove password2 e tipo_usuario do validated_data
        validated_data.pop('password2')
        tipo_usuario = validated_data.pop('tipo_usuario', 'aluno')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        # Salva o tipo de usuário no contexto para a view usar
        self.context['tipo_usuario'] = tipo_usuario
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise ValidationError('Conta desativada.')
            else:
                raise ValidationError('Credenciais inválidas.')
        else:
            raise ValidationError('Usuário e senha são obrigatórios.')
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    confirm_password = serializers.CharField(required=True, write_only=True, min_length=6)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'As novas senhas não coincidem.'
            })
        
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({
                'old_password': 'Senha atual incorreta.'
            })
        
        return data
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email não encontrado.')
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    confirm_password = serializers.CharField(required=True, write_only=True, min_length=6)
    token = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'As senhas não coincidem.'
            })
        
        # Aqui você validaria o token (em produção, implementaria lógica de token)
        # Por enquanto, apenas aceitamos qualquer token
        
        return data