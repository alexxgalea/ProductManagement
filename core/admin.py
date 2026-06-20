from django.contrib import admin

# Register your models here.
from .models import Ingredient, RecipeIngredient, Recipe, MenuItem

admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Recipe)
admin.site.register(MenuItem)

