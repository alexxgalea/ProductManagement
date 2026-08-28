from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from losses.models import ReportedLoss

from .serializers import LossSummarySerializer


# Create your views here.
class LossSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        location = request.query_params.get("location")
        if location is None:
            return Response("Acest camp este obligatoriu", status=status.HTTP_400_BAD_REQUEST)

        start = request.query_params.get("start")
        end = request.query_params.get("end")

        losses = ReportedLoss.objects.summary_by_ingredient(location=location, start=start, end=end)
        serializer = LossSummarySerializer(losses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
