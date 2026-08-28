import factory

from core.models import Ingredient


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = factory.Sequence(lambda n: f"Ingredient {n}")
    unit = "kg"
    ingredient_type = Ingredient.IngredientType.INGREDIENT
