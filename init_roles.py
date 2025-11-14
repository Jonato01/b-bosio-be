import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_backend.settings')
django.setup()

from bookings.models import Role

def create_roles():
    """Create default roles"""
    roles = ['user', 'admin', 'manager']

    for role_name in roles:
        role, created = Role.objects.get_or_create(name=role_name)
        if created:
            print(f"Created role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")

if __name__ == '__main__':
    create_roles()
    print("Roles initialization completed!")

