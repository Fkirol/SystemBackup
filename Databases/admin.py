from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Type, Frequency, Database, Backup

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('id_type', 'name')  # Campos a mostrar en la lista
    search_fields = ('name',)  # Permite buscar por nombre

@admin.register(Frequency)
class FrecuenlyAdmin(admin.ModelAdmin):
    list_display = ('id_frecuenly', 'time')  # Campos a mostrar en la lista
    search_fields = ('time',)  # Permite buscar por tiempo

@admin.register(Database)
class DatabasesAdmin(admin.ModelAdmin):
    list_display = ('id_database', 'name', 'host', 'port', 'username')  # Campos a mostrar en la lista
    search_fields = ('name', 'host', 'username')  # Permite buscar por nombre, host o usuario
    list_filter = ('id_type', 'id_frecuenly')  # Filtrar por tipo y frecuencia

@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('id_backup', 'id_database', 'date_init', 'date_finishing', 'state')  # Campos a mostrar en la lista
    search_fields = ('id_database__name', 'state')  # Permite buscar por nombre de base de datos y estado
    list_filter = ('state',)  # Filtrar por estado