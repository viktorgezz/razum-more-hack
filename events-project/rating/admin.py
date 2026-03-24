from django.contrib import admin

from .models import RatingSnapshot, PointWeight


@admin.register(RatingSnapshot)
class RatingSnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'common_rating', 'rating_it', 'rating_social', 'rating_media', 'rank', 'snapshot_date')
    list_filter = ('snapshot_date',)
    search_fields = ('user__username', 'user__email')


@admin.register(PointWeight)
class PointWeightAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'category', 'weight', 'updated_by', 'updated_at')
    list_filter = ('event_type', 'category')
    search_fields = ('event_type', 'category__name')
