from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TopProductsSerializer
from .models import ReceiptLine

# Create your views here.

class TopProductsListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        errors = {}
        location = request.query_params.get("location",None)
        limit = request.query_params.get("limit", None)
        start = request.query_params.get("start", None)
        end = request.query_params.get("end", None)

        if location is None:
            errors['location'] = "Acest camp e obligatoriu"
        
        if limit:
            limit = int(limit)
        
        if start and end:
            start = int(start)
            end = int(end)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        response = ReceiptLine.objects.top_products(location = location,
                                         limit = limit,
                                         start = start,
                                         end = end)
        
        serializer = TopProductsSerializer(response, many=True)
        
        return Response(serializer.data, status.HTTP_200_OK)