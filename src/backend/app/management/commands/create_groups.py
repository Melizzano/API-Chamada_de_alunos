# src/backend/app/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Professor, Aluno, Turma, Matricula, Presenca

class Command(BaseCommand):
    help = 'Cria grupos padrão e atribui permissões'

    def handle(self, *args, **kwargs):
        # Lista de grupos a criar
        grupos = [
            {
                'name': 'Administrador',
                'permissions': 'all'  # Todos os direitos
            },
            {
                'name': 'Coordenador',
                'permissions': [
                    'add_professor', 'change_professor', 'view_professor',
                    'add_aluno', 'change_aluno', 'view_aluno',
                    'add_turma', 'change_turma', 'view_turma',
                    'add_matricula', 'change_matricula', 'view_matricula',
                    'add_presenca', 'change_presenca', 'view_presenca',
                ]
            },
            {
                'name': 'Professor',
                'permissions': [
                    'view_professor', 'change_professor',  # Apenas seu próprio
                    'view_turma', 'change_turma',  # Apenas suas turmas
                    'view_aluno',  # Apenas alunos de suas turmas
                    'add_presenca', 'change_presenca', 'view_presenca',
                    'view_matricula',
                ]
            },
            {
                'name': 'Aluno',
                'permissions': [
                    'view_aluno', 'change_aluno',  # Apenas seu próprio
                    'view_turma',  # Apenas turmas matriculadas
                    'view_presenca',  # Apenas suas presenças
                    'view_matricula',  # Apenas suas matrículas
                ]
            },
        ]

        for grupo_info in grupos:
            grupo, created = Group.objects.get_or_create(name=grupo_info['name'])
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo criado: {grupo_info["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Grupo já existe: {grupo_info["name"]}'))
            
            # Atribuir permissões
            if grupo_info['permissions'] == 'all':
                # Todas as permissões
                grupo.permissions.set(Permission.objects.all())
            else:
                # Permissões específicas
                perms_to_add = []
                for perm_codename in grupo_info['permissions']:
                    try:
                        # Tenta encontrar a permissão
                        if '__' in perm_codename:
                            # Permissão específica de modelo (ex: view_professor)
                            app_label, model = perm_codename.split('_', 1)[1], perm_codename.split('_', 1)[0]
                            content_type = ContentType.objects.get(app_label='app', model=model)
                            perm = Permission.objects.get(
                                content_type=content_type,
                                codename=perm_codename
                            )
                            perms_to_add.append(perm)
                    except (Permission.DoesNotExist, ContentType.DoesNotExist):
                        self.stdout.write(self.style.WARNING(f'Permissão não encontrada: {perm_codename}'))
                
                if perms_to_add:
                    grupo.permissions.set(perms_to_add)
                    self.stdout.write(self.style.SUCCESS(f'  {len(perms_to_add)} permissões atribuídas'))

        self.stdout.write(self.style.SUCCESS('Grupos criados com sucesso!'))