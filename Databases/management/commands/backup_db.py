import subprocess
import os
import shutil
import getpass
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from Databases.models import Database, Backup, Frequency  # Importa tus modelos
from django.utils import timezone
import logging
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet
from django.db import transaction
from django.db.models import Q

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Establece el nivel de log deseado
handler = logging.StreamHandler()  # O FileHandler si quieres logs en un archivo
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Command(BaseCommand):
    help = 'Crea backups de las bases de datos registradas en el modelo Database y los encripta usando OpenSSL'

    #def handle(self, *args, **options):
    #    for database_instance in Database.objects.all():
    #        try:
    #            self.crear_backup_expirado()
    #            self.backup_database(database_instance)
    #        except Exception as e:
    #            logger.exception(f"Error inesperado al procesar la base de datos {database_instance.name}: {e}")
    #            # Considera si quieres continuar con las otras bases de datos o no
                
    def handle(self):
        backup_instances_actualizados = []  

        for backup_instance in Backup.objects.filter(Q(state=1) | Q(state=0), date_init__lt=timezone.now()):  
            try:
                frequency = backup_instance.id_database.id_frecuenly.time
                new_date_init = backup_instance.date_init + frequency
                
                Backup.objects.create(id_database=backup_instance.id_database,
                    date_init=new_date_init,
                    date_finishing=timezone.now(),
                    location=backup_instance.location,
                    state=1)
                
                backup_instance.state = 3
                backup_instance.save()
                
                    
                backup_instances_actualizados.append(backup_instance)
                logger.info(f"Creando las Basese de Datos...")

                self.backup_database(backup_instance.id_database)
                    
                backup_instance.state = 2
                backup_instance.date_finishing = timezone.now()
                backup_instance.save()
                    
                
                logger.info(f"Estado de la copia de seguridad {backup_instance.state}")

            except Exception as e:
                logger.exception(f"Error al crear un backup {backup_instance.id_backup}: {e}")
                backup_instance.state = 0
                backup_instance.save()
                

        return backup_instances_actualizados  
    def backup_database(self, database_instance):
        db_type = database_instance.id_type.name.lower()
        db_name = database_instance.name
        db_user = database_instance.username
        db_host = database_instance.host
        db_port = database_instance.port
        
        try:
            key = os.environ.get("ENCRYPTION_KEY")
            if key is None:
                raise ImproperlyConfigured("La clave de encriptación (ENCRYPTION_KEY) no está configurada en settings.py.")
            cipher_suite = Fernet(key)
            db_password = cipher_suite.decrypt(database_instance.password.encode()).decode()
        except Exception as e:
            raise Exception(f"Error al obtener/desencriptar la contraseña: {e}")

        # 1.1 Validación del tipo de base de datos
        valid_db_types = ['postgresql', 'mysql', 'sqlite']
        if db_type not in valid_db_types:
            msg = f'Tipo de base de datos no soportado: {db_type}'
            logger.error(msg)
           # self.crear_registro_backup(database_instance, 0, '', msg)  # Creamos el registro.
            return

        # 2. Crear el registro de backup
       # backup_record = self.crear_registro_backup(database_instance, 1)

        # 3. Construir el nombre del archivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'{db_name}_{timestamp}.sql'
        if db_type == 'postgresql':
            backup_filename += ''  # Para PostgreSQL se puede usar formato .sql o personalizado
        elif db_type == 'mysql':
            backup_filename += '.sql'

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, backup_filename)

        # 4. Construir el comando (función separada)
        try:
            command, env = self.build_command(db_type, db_name, db_user, db_host, db_port, db_password, backup_path)
        except CommandError as e:  # Errores controlados
            logger.error(str(e))
            return

        # 5. Ejecutar el comando y posteriormente encriptar el backup
        self.execute_command(command, env, db_name, backup_path, db_password)

    def build_command(self, db_type, db_name, db_user, db_host, db_port, db_password, backup_path):
        command = []
        env = os.environ.copy()  # Copia las variables de entorno existentes.

        if db_type == 'postgresql':
            pg_dump_path = shutil.which("pg_dump")
            if not pg_dump_path:
                raise CommandError("pg_dump no se encontró en el PATH. Instálalo o especifica la ruta completa.")
            command = [
                pg_dump_path,
                '-U', db_user,
                '-d', db_name,
                '-f', backup_path,
            ]
            if db_host:
                command.extend(['-h', db_host])
            if db_port:
                command.extend(['-p', str(db_port)])

        elif db_type == 'mysql':
            mysqldump_path = shutil.which("mysqldump")
            if not mysqldump_path:
                raise CommandError("mysqldump no se encontró en el PATH. Instálalo o especifica la ruta completa.")
            command = [
                mysqldump_path,
                '-u', db_user,
                db_name,
                '--result-file=' + backup_path,
                '--single-transaction',
                '--routines',
                '--triggers',
            ]
            if db_password:
                command.insert(2, f'-p{db_password}')  # Agregamos el password

        elif db_type == 'sqlite':
            db_path = db_name  # Para SQLite 'name' debe ser la ruta completa al archivo .sqlite3
            sqlite_path = shutil.which("sqlite3")
            if not sqlite_path:
                raise CommandError("sqlite3 no se encontró en el PATH. Instálalo o especifica la ruta completa.")

            command = [
                sqlite_path,
                db_path,
                f'.backup "{backup_path}"'
            ]
        return command, env




    #ENCRIPTACION
    def execute_command(self, command, env, db_name, backup_path,db_password):
        try:
            result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
            logger.info(f'Backup de {db_name} creado en: {backup_path}')
            logger.debug(f'Salida del comando: {result.stdout}')

            # 6. Encriptar el backup utilizando OpenSSL
            encryption_password = db_password
            encrypted_backup_path = backup_path + '.enc'
            openssl_command = [
                "openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
                "-in", backup_path,
                "-out", encrypted_backup_path,
                "-pass", f"pass:{encryption_password}"
            ]
            subprocess.run(openssl_command, env=env, capture_output=True, text=True, check=True)
            logger.info(f'Backup encriptado guardado en: {encrypted_backup_path}')

            # Eliminar el archivo de backup sin encriptar
            os.remove(backup_path)
            logger.debug("Archivo de backup sin encriptar eliminado.")
            
            self.store_backup(encrypted_backup_path)


        except subprocess.CalledProcessError as e:
            msg = f'Error al crear o encriptar el backup de {db_name}: {e.stderr}'
            logger.error(msg)
            logger.debug(f"Código de salida: {e.returncode}")
            logger.debug(f"Salida estándar: {e.stdout}")
    

        except FileNotFoundError as e:
            msg = f"Comando no encontrado: {e}"
            logger.error(msg)
           

    def store_backup(self, local_encrypted_path):
    # Aquí accedemos a la location

        # Encuentra el Backup relacionado al archivo actual
        filename = os.path.basename(local_encrypted_path)
        backup = Backup.objects.filter(location__isnull=False, state=1).order_by('-date_init').first()
        if not backup:
            logger.warning("No se encontró Backup en proceso para asociar la ubicación.")
            return

        destination = backup.location.strip()

        if destination.startswith('s3://'):
            # Subir a Amazon S3
            import boto3
            from urllib.parse import urlparse

            parsed = urlparse(destination)
            bucket = parsed.netloc
            key_prefix = parsed.path.lstrip('/')
            s3_key = os.path.join(key_prefix, filename)

            s3 = boto3.client('s3')
            s3.upload_file(local_encrypted_path, bucket, s3_key)
            logger.info(f"Backup subido a Amazon S3 en: s3://{bucket}/{s3_key}")

            # Borrar archivo local después de subir
            os.remove(local_encrypted_path)

        elif destination.startswith('gs://'):
            # Subir a Google Cloud Storage
            from google.cloud import storage
            from urllib.parse import urlparse

            parsed = urlparse(destination)
            bucket = parsed.netloc
            prefix = parsed.path.lstrip('/')
            gcs_blob_name = os.path.join(prefix, filename)

            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket)
            blob = bucket.blob(gcs_blob_name)
            blob.upload_from_filename(local_encrypted_path)
            logger.info(f"Backup subido a Google Cloud Storage en: gs://{bucket.name}/{gcs_blob_name}")

            # Borrar archivo local después de subir
            os.remove(local_encrypted_path)

        else:
            out_dir = os.path.abspath(destination)
            os.makedirs(out_dir, exist_ok=True)
            final_path = os.path.join(out_dir, filename)
            shutil.move(local_encrypted_path, final_path)
            logger.info(f"Backup guardado localmente en: {final_path}")

    
    
