
from rest_framework import serializers


class LossSummarySerializer(serializers.Serializer):
    name = serializers.CharField(source="ingredient__name")
    total_quantity = serializers.DecimalField(max_digits=12, decimal_places=3)
    value = serializers.DecimalField(max_digits=12, decimal_places=3)

