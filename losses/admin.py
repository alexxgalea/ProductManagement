from django.contrib import admin

from inventory.services import apply_reported_loss

from .models import ReportedLoss, StaffConsumptionBudget

# Register your models here.


@admin.action(description="Aplica pe stoc")
def apply_to_stock(modeladmin, request, queryset):
    for loss in queryset:
        apply_reported_loss(loss.id)
    modeladmin.message_user(request, f"{queryset.count()} pierderi aplicate pe stoc.")


@admin.register(ReportedLoss)
class ReportedLossAdmin(admin.ModelAdmin):
    list_display = ["location", "ingredient", "quantity", "reason", "occurred_at", "reported_by"]
    list_filter = ["location", "reason", "occurred_at"]
    search_fields = ["ingredient__name"]
    actions = [apply_to_stock]
    readonly_fields = ["applied", "applied_at"]


@admin.register(StaffConsumptionBudget)
class StaffConsumptionBudgetAdmin(admin.ModelAdmin):
    list_display = ["location", "month", "amount"]
    list_filter = ["location", "month"]
