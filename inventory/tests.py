from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from accounts.models import Location
from core.models import Ingredient
from procurement.models import Supplier, GoodsReceipt, GoodsReceiptLine
from inventory.models import Stock
from inventory.services import apply_goods_receipt


class ApplyGoodsReceiptTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name="Test", address="")
        self.ingredient = Ingredient.objects.create(
            name="Carne",
            unit="kg",
            ingredient_type=Ingredient.IngredientType.INGREDIENT,
        )
        self.stock = Stock.objects.create(
            location=self.location, ingredient=self.ingredient, quantity=Decimal("20")
        )
        supplier = Supplier.objects.create(name="Furnizor test")
        self.gr = GoodsReceipt.objects.create(
            supplier=supplier,
            location=self.location,
            date=timezone.now(),
            document_number="TEST-1",
        )
        GoodsReceiptLine.objects.create(
            goods_receipt=self.gr,
            ingredient=self.ingredient,
            quantity=Decimal("10"),
            unit_price=Decimal("30"),
        )

    def test_applies_quantity_to_stock(self):
        apply_goods_receipt(self.gr.id)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, Decimal("30"))
    
    def test_double_apply_does_not_double(self):
        apply_goods_receipt(self.gr.id)
        self.stock.refresh_from_db()
        stock_quantity_first = self.stock.quantity
        self.assertEqual(stock_quantity_first, Decimal("30"))
        apply_goods_receipt(self.gr.id)
        self.stock.refresh_from_db()
        stock_quantity_second = self.stock.quantity
        self.assertEqual(stock_quantity_first, stock_quantity_second)
