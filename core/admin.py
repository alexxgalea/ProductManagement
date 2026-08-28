from django.contrib import admin

# Register your models here.
from .models import Ingredient, MenuItem, Recipe, RecipeIngredient

admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Recipe)
admin.site.register(MenuItem)
