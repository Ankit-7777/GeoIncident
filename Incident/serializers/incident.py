from rest_framework import serializers
from Incident.models import CustomUser, Incident
import re

class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['id', 'details', 'incident_id', 'reported_date', 'reporter', 'priority', 'status', 'entity_type']
        read_only_fields = ['incident_id', 'reported_date']
    
    def validate_incident_id(self, value):
        if Incident.objects.filter(incident_id=value).exists():
            raise serializers.ValidationError("Incident ID must be unique.")
        if not re.match(r'^RMG\d{5}\d{4}$', str(value)):
            raise serializers.ValidationError("Incident ID must follow the format RMGxxxxxYYYY and be exactly 12 characters long.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            if not isinstance(request.user, CustomUser):
                raise serializers.ValidationError("Invalid user type.")
            
            if self.instance:
                if 'reporter' in data and data.get('reporter') != request.user:
                    raise serializers.ValidationError("You are not allowed to report incidents for other users.")

            if data.get('status') == 'Closed' and self.instance and self.instance.status == 'Closed':
                raise serializers.ValidationError("Cannot edit a closed incident.")
        return data
