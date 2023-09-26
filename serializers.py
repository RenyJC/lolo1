from rest_framework import serializers
from .models import Operation, FabricType, DistinctiveFeature, GarmentType

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'

class FabricTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FabricType
        fields = '__all__'

class DistinctiveFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistinctiveFeature
        fields = '__all__'

class GarmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarmentType
        fields = '__all__'
