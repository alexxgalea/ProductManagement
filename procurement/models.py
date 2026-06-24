from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import Sum , F
from django.core.validators import MinValueValidator

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=120)
    cif = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= ['cif'],
                name = "uq_cif"
            )
        ]
    def __str__(self):
        return f"{self.name} {self.cif}"
    
class GoodsReceipt(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="goods_receipts")
    location = models.ForeignKey("accounts.Location", on_delete=models.PROTECT, related_name="goods_receipts")
    date = models.DateTimeField()
    document_number = models.CharField(max_length=120)

    @property
    def total(self):
        return self.lines.aggregate(
                total=(Coalesce(
                    Sum(F("quantity") * F("unit_price"))
                    , 0, output_field=models.DecimalField()
                )
            )
        )["total"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "document_number"],
                name="uq_supplier_document_number"
            )
        ]
    def __str__(self):
        return f"{self.supplier} {self.location} {self.date} {self.document_number}"
    
    
    
class GoodsReceiptLine(models.Model):
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name="lines")
    ingredient = models.ForeignKey("core.Ingredient", on_delete=models.PROTECT, related_name="lines")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0, "Cantitatea de pe bon nu poate fi negativa")])
    unit_price = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0, "Pretul unitar nu poate fi negativ")])

    class Meta:
            constraints = [
                models.CheckConstraint(
                    condition=models.Q(quantity__gte = 0) & models.Q(unit_price__gte = 0),
                    name = "grl_quantity_unit_price_gte_0"
                )
            ]
    
    def __str__(self):
        return f"{self.goods_receipt} {self.ingredient} {self.quantity} {self.unit_price}"
    
