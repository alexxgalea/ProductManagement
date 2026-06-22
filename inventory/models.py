from django.db import models
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