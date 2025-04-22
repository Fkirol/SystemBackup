import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model

def create_superuser():
    if not User.objects.filter(is_superuser=True).exists():
        superuser = User.objects.create_superuser(
            username="admin",  # Reemplaza con el nombre de usuario deseado
            email="admin@example.com",  # Reemplaza con el correo electrónico deseado
            password="adminpassword",  # Reemplaza con la contraseña deseada (¡no uses esto en producción!)
        )
        print("Superusuario creado:", superuser.username)
    else:
        print("Superusuario ya existe.")

if __name__ == "__main__":
    create_superuser()