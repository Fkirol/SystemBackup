import subprocess
import os
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured
import boto3
from Databases.models import Database, Backup

def perform_backup_for_database(database_instance):
    # 1. Obtener información de conexión y desencriptar contraseña.
    db_type = database_instance.id_type.name.lower()
    db_name = database_instance.name
    db_user = database_instance.username
    db_host = database_instance.host
    db_port = database_instance.port

    try:
        key = settings.ENCRYPTION_KEY
        if key is None:
            raise ImproperlyConfigured("La clave de encriptación (ENCRYPTION_KEY) no está configurada en settings.py.")
        cipher_suite = Fernet(key)
        db_password = cipher_suite.decrypt(database_instance.password.encode()).decode()
    except Exception as e:
        raise Exception(f"Error al obtener/desencriptar la contraseña: {e}")

    # 2. Crear registro de Backup con estado 'Pending'
    backup_record = Backup.objects.create(
        id_database=database_instance,
        date_init=timezone.now(),
        state='Pending',
        location='',
    )

    # 3. Construir el nombre y ruta del archivo de backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'{db_name}_{timestamp}.sql'
    if db_type == 'postgresql':
        backup_filename += '.gz'
    elif db_type == 'mysql':
        backup_filename += '.sql'
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, backup_filename)

    # 4. Construir el comando según el tipo de base de datos
    command = []
    env = os.environ.copy()
    if db_type == 'postgresql':
        command = [
            'pg_dump',
            '-U', db_user,
            '-d', db_name,
            '-F', 'c',
            '-f', backup_path,
        ]
        if db_host:
            command.extend(['-h', db_host])
        if db_port:
            command.extend(['-p', str(db_port)])
        env['PGPASSWORD'] = db_password
    elif db_type == 'mysql':
        command = [
            'mysqldump',
            '-u', db_user,
            f'-p{db_password}',
            db_name,
            f'--result-file={backup_path}',
            '--single-transaction',
            '--routines',
            '--triggers',
        ]
    elif db_type == 'sqlite':
        db_path = db_name  # Para SQLite se asume que 'name' es la ruta completa
        command = [
            'sqlite3',
            db_path,
            f'.backup "{backup_path}"'
        ]
    else:
        backup_record.state = 'Failed'
        backup_record.save()
        raise Exception(f"Tipo de base de datos no soportado: {db_type}")

    # 5. Ejecutar el comando de backup
    try:
        subprocess.run(command, env=env, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        backup_record.state = 'Failed'
        backup_record.date_finishing = timezone.now()
        backup_record.save()
        raise Exception(f'Error al crear el backup de {db_name}: {e.stderr}')

    # 6. Subir a S3 (opcional)
    s3_location = upload_to_s3(backup_path, backup_filename)
    if s3_location:
        backup_record.location = s3_location
        os.remove(backup_path)
    else:
        backup_record.location = backup_path

    # 7. Actualizar registro del Backup a 'Successful'
    backup_record.date_finishing = timezone.now()
    backup_record.state = 'Successful'
    backup_record.save()