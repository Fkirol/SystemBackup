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
from .management.commands.backup_db import Command

class CrudDatabases(viewsets.ModelViewSet):
    permission_classes = [CustomAuthentication]
    serializer_class = DatabasesSerializer
    pagination_class=None
    queryset = Db.objects.all()

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
    queryset = Backup.objects.all()
    
    def get_queryset(self):
        x = Db.objects.filter(id_user=self.request.user)
        return x
    
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