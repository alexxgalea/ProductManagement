from rest_framework import serializers

class TopProductsSerializer(serializers.Serializer):
    menu_item = serializers.IntegerField()
    name = serializers.CharField(max_length = 120 , source = "menu_item__name")
    qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    revenue = serializers.DecimalField(max_digits=24, decimal_places=6)
