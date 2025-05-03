from Auth.views import CustomAuthentication
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Database as Db, Backup
from .serializer import DatabasesSerializer,BackupsSerializer, BackupsSeria
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .management.commands.backup_db import Command

class CrudDatabases(viewsets.ModelViewSet):
    permission_classes = [CustomAuthentication]
    serializer_class = DatabasesSerializer
    pagination_class=None
    #queryset = Db.objects.all()

    def get_queryset(self):
        x = Db.objects.filter(id_user=self.request.user)
        return x
    
    

class ListBackups(ListAPIView):
    permission_classes = [CustomAuthentication]
    serializer_class = BackupsSerializer
    
    def get_queryset(self):
        id_database = self.kwargs.get('id_database')
        
        user = Db.objects.filter(id_database=id_database).values("id_user").first()
        
        
        if int(user['id_user']) != int(self.request.user):
            raise PermissionDenied
       
        return Backup.objects.filter(id_database=id_database).order_by('date_init')
    
class BackupView(viewsets.ModelViewSet):
    permission_classes = [CustomAuthentication]
    serializer_class = BackupsSeria
    pagination_class=None
    
    def get_queryset(self):
        x = Backup.objects.filter(id_user=self.request.user)
        return x
    
def download_local_backup(request, db_id):
    
    db = get_object_or_404(Db, pk=db_id)
    db_type = db.id_type.name.lower()

    # 1) Desencriptar la contraseña de la DB (almacenada en el modelo)
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise Http404("Falta ENCRYPTION_KEY en el servidor")
    db_pwd = Fernet(key).decrypt(db.password.encode()).decode()
    print(Fernet(key).decrypt(db.password.encode()).decode())

    # 2) Nombre de fichero que verá el usuario
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{db.name}_{ts}.sql.enc"

    # 3) Construir comando de dump hacia stdout
    env = os.environ.copy()
    if db_type == "postgresql":
        pg_dump = shutil.which("pg_dump")
        if not pg_dump:
            raise Http404("pg_dump no disponible en el servidor")
        # Insertamos la contraseña en la URI de conexión:
        host = db.host or "localhost"
        port = db.port or 5432
        uri = f"postgresql://{db.username}:{db_pwd}@{host}:{port}/{db.name}"
        dump_cmd = [pg_dump, f"--dbname={uri}"]

    elif db_type == "mysql":
        mysqldump = shutil.which("mysqldump")
        if not mysqldump:
            raise Http404("mysqldump no disponible en el servidor")
        # Metemos el password en el flag -p para que mysqldump lo use
        dump_cmd = [
            mysqldump,
            "-u", db.username,
            f"-p{db_pwd}",
            db.name,
            "--single-transaction",
            "--routines",
            "--triggers",
        ]
        if db.host:
            dump_cmd += ["-h", db.host]
        if db.port:
            dump_cmd += ["-P", str(db.port)]

    elif db_type == "sqlite":
        sqlite3_bin = shutil.which("sqlite3")
        if not sqlite3_bin:
            raise Http404("sqlite3 no disponible en el servidor")
        # .dump volcará todo el SQL por stdout
        dump_cmd = [sqlite3_bin, db.name, ".dump"]

    elif db_type == "mongodb":
        mongodump = shutil.which("mongodump")
        if not mongodump:
            raise Http404("mongodump no disponible en el servidor")
        # Usamos URI para pasar user:pass@host:port/db
        host = db.host or "localhost"
        port = db.port or 27017
        uri = f"mongodb://{db.username}:{db_pwd}@{host}:{port}/{db.name}"
        dump_cmd = [mongodump, "--uri", uri, "--archive", "--gzip"]

    else:
        raise Http404(f"Tipo de base de datos no soportado: {db.id_type.name}")

    # 4) Comando de OpenSSL para cifrar en AES-256-CBC con PBKDF2+salt
    print(db_pwd)
    openssl_cmd = [
        "openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
        "-pass", f"pass:{db_pwd}"
    ]

    # 5) Pipeline: dump_cmd | openssl_cmd → StreamingHttpResponse
    p1 = subprocess.Popen(dump_cmd, env=env, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(openssl_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()

    response = StreamingHttpResponse(
        p2.stdout,
        content_type="application/octet-stream"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
    
@method_decorator(csrf_exempt, name='dispatch')
class RunBackupAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Ejecuta el comando de backup
            cmd = Command()
            cmd.handle()
            return Response({"message": "Backup iniciado correctamente"}, status=status.HTTP_200_OK)
        except Exception as e:
            # Registra el error o envía notificaciones si es necesario
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.decorators import action
import os
import shutil
import subprocess
from datetime import datetime
from django.http import StreamingHttpResponse, Http404
from django.conf import settings
from cryptography.fernet import Fernet


