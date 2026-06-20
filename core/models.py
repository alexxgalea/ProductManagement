from django.db import models
from django.db.models import UniqueConstraint
# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=20)
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=3)

    def __str__(self):
        return f"{self.name} ({self.unit} {self.quantity_on_hand})"
    
class MenuItem(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name
    
class Recipe(models.Model):
    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reteta pentru {self.menu_item.name}"

# childOf --> CASCADE
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="lines", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields= ["recipe", "ingredient"], name="uq_receipe_ingredient"
            )
        ]

    def __str__(self):
        return f"Linie rețetă: {self.recipe.menu_item.name} -> {self.ingredient.name} ({self.quantity})"