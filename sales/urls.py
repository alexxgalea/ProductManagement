from django.urls import path
from .views import TopProductsListAPIView

urlpatterns = [
    path('top-products/', view=TopProductsListAPIView.as_view(), name='top-products')
]