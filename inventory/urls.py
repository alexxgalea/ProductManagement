from django.urls import path
from .views import InventoryDiscrepancyView, StockReportView, StockValueView

urlpatterns = [
    path("stock/", StockReportView.as_view(), name="stock"),
    path("stock/value/", StockValueView.as_view(), name="stock_value"),
    path("inventory/discrepancy/", InventoryDiscrepancyView.as_view(), name="inventory_discrepancy")
]