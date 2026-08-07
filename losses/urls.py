from .views import LossSummaryView
from django.urls import path

urlpatterns = [
    path("losses/summary/", LossSummaryView.as_view(), name="losses-summary"),
]
