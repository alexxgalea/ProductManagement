from django.contrib import admin

from .models import Stock, StockCount, StockCountLine
from .services import apply_stock_count

# Register your models here.

admin.site.register(Stock)


@admin.action(description="Aplica pe stoc")
def apply_to_stock(modeladmin, request, queryset):
    for sc in queryset:
        apply_stock_count(sc.id)
    modeladmin.message_user(request, f"{queryset.count()} inventare aplicate pe stoc")


class StockCountLineInLine(admin.TabularInline):
    model = StockCountLine
    extra = 3
    show_change_link = True
    readonly_fields = ["variance"]


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = ["location", "date"]
    search_fields = ["location__name"]
    actions = [apply_to_stock]
    readonly_fields = ["applied", "applied_at"]

    inlines = [StockCountLineInLine]
