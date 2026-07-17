from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Stock, StockCount
from .serializers import StockReportSerializer, StockCountLineSerializer
from django.db.models import Sum

# Create your views here.
class StockReportView(APIView):
    def get(self, request):
        location = request.query_params.get("location")
        if location is None:
            return Response({"location": "Acest camp este obligatoriu"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        stocks = Stock.objects.with_value().filter(location=location)
        serializer = StockReportSerializer(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class StockValueView(APIView):
    def get(self,request):
        location = request.query_params.get("location")
        if location is None:
            return Response({"location": "Acest camp este obligatoriu"}, 
                            status = status.HTTP_400_BAD_REQUEST)
        total = (Stock.objects.with_value().filter(location=location).aggregate(total = Sum("value"))["total"])

        return Response({"location": location, "total": total or 0}, status=status.HTTP_200_OK)
    
class InventoryDiscrepancyView(APIView):
    def get(self, request):
        location = request.query_params.get("location")
        if location is None:
            return Response({"location": "Acest camp este obligatoriu"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        last_count = StockCount.objects.filter(location=location).order_by('-date').first()
        if last_count is None:
            return Response([], status=status.HTTP_200_OK)
        
        lines =  last_count.stock_lines.all()
        serializer = StockCountLineSerializer(lines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)