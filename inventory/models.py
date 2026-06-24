from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.contrib import admin
# Create your models here.

class Stock(models.Model):
    location = models.ForeignKey("accounts.Location", on_delete=models.CASCADE, related_name="stocks")
    ingredient = models.ForeignKey("core.Ingredient", on_delete=models.PROTECT, related_name="stocks")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location} {self.ingredient} {self.quantity}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["location", "ingredient"],
                name = "uq_location_ingredient"
            )
            
        ]
    
    @property
    def is_negative(self):
        return self.quantity < 0
    


class StockCount(models.Model):
    location = models.ForeignKey("accounts.Location", on_delete=models.PROTECT, related_name="stock_counts")
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.location} {self.date}"
    

class StockCountLine(models.Model):
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name="stock_lines", validators=[MinValueValidator(0.0, "Cantitatea nu poate fi negativa")])
    ingredient = models.ForeignKey("core.Ingredient", on_delete=models.PROTECT, related_name="stock_lines")
    counted_quantity = models.DecimalField(max_digits=12, decimal_places=3)

    @property
    @admin.display(description="Discrepanta")
    def variance(self):
        location = self.stock_count.location
        if self.counted_quantity is None or self.stock_count_id is None:
            return None

        try:
            stock_record = Stock.objects.get(location=location, ingredient=self.ingredient)
            current_stock = stock_record.quantity
        except ObjectDoesNotExist:
            current_stock = Decimal("0.000")

        return self.counted_quantity - current_stock


    class Meta:
        constraints = [
            models.CheckConstraint(
                condition= models.Q(counted_quantity__gte=0),
                name="counted_quantity_gte_0"
            ),
            models.UniqueConstraint(
                fields=["stock_count", "ingredient"],
                name="uq_stock_count_ingredient"
            )
        ]
    def __str__(self):
        return f"{self.stock_count} {self.ingredient} {self.counted_quantity}"