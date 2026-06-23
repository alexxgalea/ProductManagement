from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Ingredient(models.Model):
    class IngredientType(models.TextChoices):
        INGREDIENT = "INGREDIENT", "Ingredient"
        CONSUMABLE =  "CONSUMABIL", "Consumabil"

    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=20)
    unitary_cost = models.DecimalField(max_digits=12, decimal_places=5,null=True,blank=True, validators=[MinValueValidator(0.0, "Costul unitar nu poate fi negativ")])
    ingredient_type = models.CharField (choices= IngredientType, max_length= 20, default=IngredientType.INGREDIENT)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(unitary_cost__gte=0.0) | models.Q(unitary_cost__isnull=True),
                name = "unitary_cost_gte_0_or_null"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.unit} {self.unitary_cost} {self.ingredient_type})"
    
class MenuItem(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name
    
class Recipe(models.Model):
    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reteta pentru {self.menu_item.name}"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="lines", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    net_quantity = models.DecimalField(max_digits=12, decimal_places=3)
    loss_factor = models.DecimalField(max_digits=3, decimal_places=2, 
                                       validators=[MinValueValidator(0.0, message="Factorul nu poate fi negativ"),
                                                   MaxValueValidator(1.0, message="Factorul nu poate fi mai mare decat 1")], default=0)
    
    @property
    def gross_quantity(self):
        return self.net_quantity * (1 + self.loss_factor)
    
    @property
    def cost(self):
        if self.ingredient.unitary_cost is None:
            return None
        return self.gross_quantity * self.ingredient.unitary_cost


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= ["recipe", "ingredient"], name="uq_receipe_ingredient"
            ),
            models.CheckConstraint(
                condition=models.Q(loss_factor__gte=0.0) & models.Q(loss_factor__lte=1.0),
                name="loss_factor_between_0_and_1"
            )
        ]

    def __str__(self):
        return f"Linie rețetă: {self.recipe.menu_item.name} -> {self.ingredient.name} ({self.net_quantity} {self.loss_factor})"