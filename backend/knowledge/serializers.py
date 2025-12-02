from rest_framework import serializers
from .models import KnowledgeConfig

class KnowledgeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeConfig
        fields = '__all__'
