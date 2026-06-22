from django.contrib import admin
from .models import Receipt, ReceiptLine
# Register your models here.

admin.site.register(Receipt)
admin.site.register(ReceiptLine)