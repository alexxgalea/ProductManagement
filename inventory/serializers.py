from rest_framework import serializers


class StockReportSerializer(serializers.Serializer):
    name = serializers.CharField(source="ingredient.name")
    unit = serializers.CharField(source="ingredient.unit")
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3)
    value = serializers.DecimalField(max_digits=14, decimal_places=2)


class StockCountLineSerializer(serializers.Serializer):
    name = serializers.CharField(source="ingredient.name")
    counted_quantity = serializers.DecimalField(max_digits=12, decimal_places=3)
    variance = serializers.DecimalField(max_digits=12, decimal_places=3)
