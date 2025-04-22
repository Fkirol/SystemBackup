from rest_framework import serializers
from .models import Database,Backup,Frequency


class DatabasesSerializer(serializers.ModelSerializer):
    id_database = serializers.IntegerField(read_only=True) 
    time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Database
        fields = ['time','id_database','name', 'id_type', 'host', 'port', 'username', 'password', 'id_frecuenly']
    
    def get_time(self, obj):
        backups = Backup.objects.filter(id_database=obj.id_database).order_by('-date_init').values('date_init','date_finishing')[:2]

        time = dict()

        if backups:  # Check if the list is not empty
            time['date_finishing'] = backups[0]['date_init']  # Safely access the first element

            if len(backups) == 2:
                time['date_init'] = backups[1]['date_finishing']
            elif len(backups) == 1:
                time['date_init'] = None #O algun valor default que quieras usar
            else:
                time['date_init'] = None #O algun valor default que quieras usar
        else:
            # Handle the case where there are no backups
            time['date_init'] = None  # Or some default value
            time['date_finishing'] = None  # Or some default value

        return time

    def create(self, validated_data):
        validated_data['id_user'] = self.context['request'].user
        return super().create(validated_data)   
    
    
class BackupsSerializer(serializers.ModelSerializer):
    id_backup = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Backup
        fields = ['date_init','date_finishing','state','location','id_backup']
        
class BackupsSeria(serializers.ModelSerializer):
    id_backup = serializers.IntegerField(read_only=True)
    state = serializers.IntegerField(read_only=True)
    class Meta:
        model = Backup
        fields = '__all__'

        
        
class FrequencySerializer(serializers.ModelSerializer):
    id_frecuenly = serializers.IntegerField()
    
    class Meta:
        model = Frequency
        fields = '__all__'