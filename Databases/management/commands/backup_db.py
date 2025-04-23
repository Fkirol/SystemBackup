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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Establece el nivel de log deseado
handler = logging.StreamHandler()  # O FileHandler si quieres logs en un archivo
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Command(BaseCommand):
    help = 'Crea backups de las bases de datos registradas en el modelo Database y los encripta usando OpenSSL, en paralelo'

    def handle(self, *args, **options):
        # 1. Recuperamos solo los backups pendientes/expirados
        backups = Backup.objects.filter(state__in=[0,1], date_init__lt=timezone.now())

        # 2. Creamos un pool de hilos
        max_workers = min(5, backups.count())  # ajusta grado de paralelismo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 3. Para cada instancia de backup lanzamos submit() que disparará backup_database()
            future_to_backup = {
                executor.submit(self._run_backup_workflow, b): b
                for b in backups
            }

            # 4. Opcionalmente, esperamos a que vayan terminando y registramos
            for future in as_completed(future_to_backup):
                b = future_to_backup[future]
                try:
                    future.result()
                    logger.info(f"[{b.id_backup}] Backup terminado correctamente.")
                except Exception as e:
                    logger.error(f"[{b.id_backup}] Error en hilo de backup: {e}")

    def _run_backup_workflow(self, backup_instance):
        try:
            frequency = backup_instance.id_database.id_frecuenly.time
            new_date_init = backup_instance.date_init + frequency
                
            Backup.objects.create(id_database=backup_instance.id_database,
                date_init=new_date_init,
                date_finishing=timezone.now(),
                location=backup_instance.location,
                state=1)
            db = backup_instance.id_database
        
            
            backup_instance.state = 3 
            backup_instance.save()

            # Ejecuta backup + encriptado
            self.backup_database(db)
            logger.info(f"Creando la Base De Datos...")
            

            # al terminar:
            backup_instance.state = 2  # Successful
            backup_instance.date_finishing = timezone.now()
            backup_instance.save()
        except Exception as e:
            logger.exception(f"Error al crear un backup {backup_instance.id_backup}: {e}")
            backup_instance.state = 0
            backup_instance.save()

                

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
            return


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
            
        elif db_type == 'mongodb':
            mongodump = shutil.which("mongodump")
            if not mongodump:
                raise CommandError("mongodump no encontrado en el PATH.")
            dump_dir = backup_path.replace('.gz', '')  # Mongo crea carpetas
            command = [
                mongodump,
                f'--username={db_user}',
                f'--password={db_password}',
                f'--db={db_name}',
                f'--out={dump_dir}'
            ]
            if db_host:
                command += [f'--host={db_host}']
            if db_port:
                command += [f'--port={db_port}']
            env["MONGODB_URI"] = f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        else:
            raise CommandError(f"Tipo de base de datos no soportado: {db_type}")
        return command, env




    #ENCRIPTACION
    def execute_command(self, command, env, db_name, backup_path,db_password,**kwargs):
        try:
            result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
            logger.info(f'Backup de {db_name} creado en: {backup_path}')
            logger.debug(f'Salida del comando: {result.stdout}')
            
            db_type = kwargs.get('db_type', 'unknown')
            
            if db_type == 'mongodb':
                import tarfile
                tar_path = backup_path + ".tar.gz"
                with tarfile.open(tar_path, "w:gz") as tar:
                    tar.add(backup_path, arcname=os.path.basename(backup_path))
                backup_path = tar_path  # usamos el tar.gz para cifrar

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


        except subprocess.CalledProcessError as e:
            msg = f'Error al crear o encriptar el backup de {db_name}: {e.stderr}'
            logger.error(msg)
            logger.debug(f"Código de salida: {e.returncode}")
            logger.debug(f"Salida estándar: {e.stdout}")
    

        except FileNotFoundError as e:
            msg = f"Comando no encontrado: {e}"
            logger.error(msg)
           

    
