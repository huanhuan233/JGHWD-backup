from rest_framework import serializers
from .models import Outline

class OutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outline
        fields = '__all__'
