from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.functions import Coalesce
from django.db.models import Sum, F


# Create your models here.

class Receipt(models.Model):
    location = models.ForeignKey("accounts.Location", on_delete=models.PROTECT, related_name="receipts")
    sold_at = models.DateTimeField()
    external_id = models.CharField(max_length=64)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["location", "external_id"],
                name = "uq_location_external_id"
            )
        ]
    
    @property
    def total(self):
        return self.lines.aggregate(
                total=(Coalesce(
                    Sum(F("quantity") * F("unit_price"))
                    , 0, output_field=models.DecimalField()
                )
            )
        )["total"]
    
    def __str__(self):
        return f"{self.location} {self.sold_at} {self.external_id}"
    
class ReceiptLineQuerySet(models.QuerySet):
    def top_products(self, location=None, start=None, end=None, limit=10):
        qs = self
        if location is not None:
            qs = self.filter(receipt__location = location)
        if start is not None and end is not None:
            qs = qs.filter(receipt__sold_at__range=(start,end))
        
        return(qs.values("menu_item","menu_item__name")
               .annotate(qty = Sum("quantity"),
                         revenue = Sum(F("quantity")*F("unit_price"), 
                                       output_field = models.DecimalField()),
                         ).order_by("-qty")[:limit])

class ReceiptLine(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="lines")
    menu_item = models.ForeignKey("core.MenuItem", on_delete=models.PROTECT, related_name="lines")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0, "Cantitatea de pe bon nu poate fi negativa")])
    unit_price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0, "Pretul unitar nu poate fi negativ")])

    objects = ReceiptLineQuerySet.as_manager()
    def __str__(self):
        return f"{self.receipt} {self.menu_item} {self.quantity} {self.unit_price}"
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition = models.Q(quantity__gte = 0) & models.Q(unit_price__gte = 0),
                name="quantity_unit_price_gte_0"),
            
            models.UniqueConstraint(
                fields = ["receipt","menu_item"],
                name = "uq_receipt_menu_item"
            )
        ]