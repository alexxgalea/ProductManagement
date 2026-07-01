from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

# Create your models here.
class ReportedLoss(models.Model):
    class Reason(models.TextChoices):
        expired = "EXPIRAT", "Expirat"
        burned = "ARS", "Ars"
        rotten = "STRICAT", "Stricat"
        dropped = "SCAPAT", "Scapat"

        
    location = models.ForeignKey("accounts.Location", on_delete=models.PROTECT, related_name="reported_losses")
    ingredient = models.ForeignKey("core.Ingredient", on_delete=models.PROTECT, related_name="reported_losses")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.0, message="Cantitatea nu poate fi negativa")])
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,blank=True, on_delete=models.SET_NULL)
    occurred_at = models.DateTimeField(default=timezone.now)

    class Meta:
            constraints = [
                models.CheckConstraint(
                    condition=models.Q(quantity__gte=0.0),
                    name = "reportedloss_quantity_gte_0"
                )
            ]
            
    def __str__(self):
        return f"{self.location} {self.ingredient} {self.quantity}"
