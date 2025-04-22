import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')  # Cambia 'mi_proyecto' al nombre de tu proyecto
django.setup()

from Databases.models import Database,Backup
from datetime import datetime



databases = list(Database.objects.all())

for i in databases:
    backup = Backup()
    backup.id_database = i
    backup.date_init = datetime.now() + i.id_frecuenly.time
    backup.location = "https://www.google.com"
    backup.state = "Success"
    backup.save()

