from django.urls import path

from .views import LossSummaryView

urlpatterns = [
    path("losses/summary/", LossSummaryView.as_view(), name="losses-summary"),
]
