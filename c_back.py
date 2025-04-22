#!/usr/bin/env python3
import os
import subprocess
import getpass
import logging
from datetime import datetime

# Configuración del logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_backup(db_name, db_user, db_host, db_port, output_path):
    """
    Crea un backup de PostgreSQL usando pg_dump.
    
    Args:
        db_name (str): Nombre de la base de datos.
        db_user (str): Usuario de PostgreSQL.
        db_host (str): Host del servidor.
        db_port (str): Puerto del servidor.
        output_path (str): Ruta donde se guardará el backup.
    
    Returns:
        bool: True si el backup se creó correctamente, False en caso de error.
    """
    try:
        # Definir la ruta completa del comando pg_dump
        pg_dump_path = "pg_dump"

        # Crear el comando de respaldo
        command = [
            pg_dump_path,
            "-U", db_user,
            "-h", db_host,
            "-p", str(db_port),
            "-F", "c",  # Formato personalizado (más eficiente y compatible)
            "-f", output_path,
            db_name
        ]

        # Configurar variables de entorno para la contraseña
        env = os.environ.copy()
        env["PGPASSWORD"] = getpass.getpass("Introduce la contraseña de la base de datos: ")

        # Ejecutar el comando
        subprocess.run(command, env=env, check=True)
        logger.info(f"Backup creado con éxito: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al crear el backup: {e}")
        return False

def encrypt_backup(backup_path, encrypted_path):
    """
    Encripta un archivo de backup utilizando OpenSSL AES-256-CBC.
    
    Args:
        backup_path (str): Ruta del archivo de backup sin encriptar.
        encrypted_path (str): Ruta donde se guardará el backup encriptado.
    """
    try:
        # Solicitar contraseña de encriptación de manera segura
        encryption_password = getpass.getpass("Introduce la contraseña para encriptar el backup: ")

        # Comando de OpenSSL para encriptar con AES-256-CBC
        command = [
            "openssl", "enc", "-aes-256-cbc",
            "-salt", "-pbkdf2",
            "-in", backup_path,
            "-out", encrypted_path,
            "-pass", f"pass:{encryption_password}"
        ]

        # Ejecutar la encriptación
        subprocess.run(command, check=True)
        logger.info(f"Backup encriptado con éxito: {encrypted_path}")

        # Eliminar el archivo original por seguridad
        os.remove(backup_path)
        logger.info("Archivo de backup sin encriptar eliminado.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al encriptar el backup: {e}")

def main():
    # Configuración de la base de datos
    DB_NAME = "mi_base_de_datos"
    DB_USER = "mi_usuario"
    DB_HOST = "localhost"
    DB_PORT = 5432  # Puerto por defecto de PostgreSQL

    # Generar nombre del archivo de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{DB_NAME}_{timestamp}.dump"
    encrypted_filename = f"{backup_filename}.enc"

    # Definir las rutas
    backup_path = os.path.join(os.getcwd(), backup_filename)
    encrypted_path = os.path.join(os.getcwd(), encrypted_filename)

    # Crear y encriptar el backup
    if create_backup(DB_NAME, DB_USER, DB_HOST, DB_PORT, backup_path):
        encrypt_backup(backup_path, encrypted_path)

if __name__ == "__main__":
    main()
