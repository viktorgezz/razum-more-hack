from django.contrib import admin

from rating.models import PointWeight


@admin.register(PointWeight)
class PointWeightAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "category", "weight", "updated_by", "updated_at")
    list_filter = ("event_type", "category")
    search_fields = ("event_type", "category__name", "category__slug")
