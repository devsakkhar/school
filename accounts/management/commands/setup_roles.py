from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Creates default roles and assigns basic permissions.'

    def handle(self, *args, **kwargs):
        # Define the roles and their corresponding permissions
        # We assign permissions based on codename
        roles_data = {
            'Admin': [
                'manage_roles', 'manage_users', 'view_dashboard_stats',
                'manage_academic_settings', 'manage_finances'
            ],
            'Teacher': [
                'view_dashboard_stats',
            ],
            'Student': [
            ],
        }

        self.stdout.write(self.style.NOTICE('Starting default roles setup...'))

        for role_name, perms in roles_data.items():
            role, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Role already exists: {role_name}'))

            # Assign permissions
            for perm_codename in perms:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    role.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Permission {perm_codename} not found!'))

            self.stdout.write(self.style.SUCCESS(f'Successfully assigned permissions to {role_name}'))

        self.stdout.write(self.style.SUCCESS('Role setup complete.'))
