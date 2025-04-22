import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings")
django.setup()


from django.contrib.auth.hashers import make_password 
from django.contrib.auth import get_user_model

User = get_user_model() # Obten el modelo de usuario configurado
   
try:
    User.objects.get(username='admin')
except:
    User.objects.create_superuser(
        username="admin",
        password="admin",        
    )
 
