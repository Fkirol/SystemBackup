from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')  # Campos a mostrar en la lista
    search_fields = ('status',)  # Permite buscar por nombre

