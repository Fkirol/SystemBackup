import os
import sys
import base64
import getpass
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configuración básica del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Deriva una clave para Fernet a partir de una contraseña y un salt.

    Args:
        password (str): La contraseña.
        salt (bytes): Salt aleatorio.

    Returns:
        bytes: Clave derivada en formato url-safe.
    """
    kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def decrypt_backup(encrypted_backup_path: str, output_path: str, db_password: str):
    """
    Desencripta un backup encriptado utilizando la contraseña de la base de datos.
    El archivo encriptado debe tener el salt (16 bytes) concatenado al inicio.

    Args:
        encrypted_backup_path (str): Ruta del archivo encriptado.
        output_path (str): Ruta donde se guardará el backup desencriptado.
        db_password (str): Contraseña de la base de datos utilizada para encriptar.
    """
    try:
        # Leer el contenido del archivo encriptado
        with open(encrypted_backup_path, 'rb') as f:
            content = f.read()

        if len(content) < 16:
            raise ValueError("El archivo encriptado no contiene el salt necesario.")

        # Extraer el salt (primeros 16 bytes) y el contenido encriptado
        salt = content[:16]
        encrypted_data = content[16:]
        logger.debug(f"Salt extraído: {salt.hex()}")

        # Derivar la clave usando la contraseña de la base de datos y el salt
        key = derive_key(db_password, salt)
        cipher = Fernet(key)

        # Desencriptar el contenido
        decrypted_data = cipher.decrypt(encrypted_data)

        # Escribir el backup desencriptado en el archivo de salida
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        logger.info(f"Desencriptación exitosa. Archivo desencriptado guardado en: {output_path}")

    except Exception as e:
        logger.error(f"Error al desencriptar el backup: {e}")
        sys.exit(1)

def main():
    # Definir las rutas de los archivos
    encrypted_file = "C:\\Users\\Fer\\Desktop\\Databases Backup System\\Backend\\backups\\railway_20250331_104337.sql.enc"  # Reemplaza con la ruta correcta
    output_file = "C:\\Users\\Fer\\Desktop\\Databases Backup System\\Backend\\backups\\railwa_20250331_104337.sql"  # Reemplaza con la ruta correcta

    # Si deseas que la contraseña se ingrese de forma interactiva (oculta), se puede hacer así:
    db_password = "KtQblVvPDWRYCKmhgLxeJycHzCInSkOk"

    if not os.path.exists(encrypted_file):
        logger.error(f"El archivo encriptado '{encrypted_file}' no existe.")
        sys.exit(1)

    decrypt_backup(encrypted_file, output_file, db_password)

if __name__ == '__main__':
    main()