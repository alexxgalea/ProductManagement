from django.contrib import admin
from .models import Stock, StockCount, StockCountLine
# Register your models here.

admin.site.register(Stock)

class StockCountLineInLine(admin.TabularInline):
    model = StockCountLine
    extra = 3
    show_change_link = True
    readonly_fields = ["variance"]

@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = ["location","date"]
    search_fields = ["location__name"]

    inlines = [StockCountLineInLine]