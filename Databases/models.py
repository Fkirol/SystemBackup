from typing import Iterable
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidKey
import os
from django.utils import timezone

# Create your models here.
class Type(models.Model):
    id_type=models.AutoField(primary_key=True,)
    name=models.CharField(max_length=30,)
    
class Frequency(models.Model):
    id_frecuenly = models.AutoField(primary_key=True,)
    time = models.DurationField()
    
class Database(models.Model):
    id_database = models.AutoField(primary_key=True,)
    
    id_type=models.ForeignKey(Type,on_delete=models.CASCADE)
    id_user=models.CharField(max_length=1,default=1)
    id_frecuenly = models.ForeignKey(Frequency,on_delete=models.CASCADE)    
    
    
    name = models.CharField(max_length=150)
    host = models.CharField(max_length=100)
    port = models.IntegerField(default=5432)  # Por defecto para PostgreSQL
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=200)  # Considera encriptar la contraseña
    
    
    def __str__(self) -> str:
        return self.name
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        encryption_key = os.environ.get("ENCRYPTION_KEY")
        if encryption_key is None:
            raise ImproperlyConfigured("ENCRYPTION_KEY environment variable not set.")

        # Asegurarse de que la clave sea de tipo bytes
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode('utf-8')

        self.fernet = Fernet(encryption_key)
        
    def __setattr__(self, name, value):
        """
        Intercepta la asignación al campo 'password' para guardar
        la versión sin cifrar en '_password'.
        """
        if name == 'password':
            self._password = value  
        super().__setattr__(name, value)

    
    def save(self, *args, **kwargs):
        if self._password is not None:
            self.password = self.encrypt_password(self._password)
            self._password = None  
        super().save(*args, **kwargs)
        
    def encrypt_password(self, password):
        """Cifra la contraseña usando Fernet."""
        return self.fernet.encrypt(password.encode('utf-8')).decode('utf-8')

    def decrypt_password(self, encrypted_password):
        """Descifra la contraseña usando Fernet."""
        try:
            return self.fernet.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')
        except InvalidKey:
            raise ValueError("Invalid decryption key or corrupted ciphertext.")
    
    
    
class Backup(models.Model):
    class Status(models.IntegerChoices):
        FAILED = 0, 'FAILED'
        PENDING = 1, 'PENDING'
        SUCCESSFUL = 2, 'SUCCESSFUL'
        IN_PROCESS = 3, 'IN_PROCESS'
    id_backup = models.AutoField(primary_key=True,)
    
    id_database = models.ForeignKey(Database,on_delete=models.CASCADE,)
    
    date_init = models.DateTimeField(default=timezone.now)
    date_finishing = models.DateTimeField(null=True)
    
    location = models.URLField(max_length=200)
    
    state = models.IntegerField(choices=Status.choices, default=Status.PENDING)
    
    

    



   
# postgresql://postgres:KtQblVvPDWRYCKmhgLxeJycHzCInSkOk@autorack.proxy.rlwy.net:24073/railway