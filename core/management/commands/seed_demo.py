from django.core.management.base import BaseCommand
from accounts.models import Location
from sales.models import Receipt, ReceiptLine
from core.models import Ingredient, RecipeIngredient, Recipe, MenuItem
from inventory.models import Stock
import random
from decimal import Decimal
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    help = "Used to populate the db with test data"

    def add_arguments(self, parser):
        parser.add_argument('receipts', type=int, help="How many receipts to be added", default=3)
        parser.add_argument('receipt_lines', type=int, help="How many receipt lines to be added", default=3)
        parser.add_argument('ingredients', type=int, help="How many ingredients to be added", default=3)
        parser.add_argument('--flush', action="store_true", help="Deletes the previous data")
    
    @transaction.atomic
    def handle(self, *args, **opts):

        random.seed(42)
        nof_receipts = opts["receipts"]
        nof_receipts_lines = opts["receipt_lines"]
        nof_ingredients = opts["ingredients"]
        flush = opts["flush"]

        if flush:
            Receipt.objects.all().delete()
            Location.objects.all().delete()
            RecipeIngredient.objects.all().delete()
            Ingredient.objects.all().delete()
            MenuItem.objects.all().delete()
            ReceiptLine.objects.all().delete()
            Recipe.objects.all().delete()
           
            Stock.objects.all().delete

        new_location, _ = Location.objects.get_or_create(name="Locatie demo", 
                                                         address = "Adresa noua")
       
        ingredients= [Ingredient.objects.get_or_create(name=f"Ingredient {i}", 
                                                       unit="g", 
                                                       unitary_cost = Decimal(i) + Decimal("0.05"), 
                                                       ingredient_type = Ingredient.IngredientType.INGREDIENT)[0]
                      for i in range(nof_ingredients)]
        
        menu_items = [MenuItem.objects.get_or_create(name = f"Element de meniu {i}")[0]
                      for i in range(nof_receipts_lines)]
        recipes = []
        for menu_item in menu_items:
            recipe = Recipe.objects.get_or_create(menu_item = menu_item)[0]
            recipes.append(recipe)

        recipe_ingredients = []
        ri = 0
        for recipe in recipes:
            for ingredient in ingredients:
                rand_float = random.uniform(0.0,0.3)
                rand_decimal = Decimal(str(rand_float)).quantize(Decimal('0.01'))
                recipe_ingredients.append(RecipeIngredient(recipe = recipe, 
                                                           ingredient = ingredient ,
                                                           net_quantity = Decimal(ri) + Decimal("0.08"), 
                                                           loss_factor = rand_decimal + Decimal("0.09")))
                ri+=1
        RecipeIngredient.objects.bulk_create(recipe_ingredients, 
                                             ignore_conflicts=True)

        receips = [Receipt.objects.get_or_create(location = new_location, 
                                                 sold_at = timezone.now(), 
                                                 external_id = f"Identificator{i}")[0]
                   for i in range(nof_receipts)]
        
        receipt_lines = []
        rl = 0
        for receipt in receips:
            for menu_item in menu_items:
                receipt_lines.append(ReceiptLine(receipt = receipt, 
                                                 menu_item = menu_item, 
                                                 quantity = Decimal(rl) + Decimal("0.06"), 
                                                 unit_price = Decimal(rl) + Decimal("0.07") ))
                rl+=1
        ReceiptLine.objects.bulk_create(receipt_lines,
                                        ignore_conflicts=True)
        
        stocks = []
        for i, ingredient in enumerate(ingredients):
            stocks.append(Stock(location=new_location, 
                                ingredient = ingredient, 
                                quantity = Decimal(i) + Decimal("0.12")))
        
        Stock.objects.bulk_create(stocks,
                                  ignore_conflicts=True)
