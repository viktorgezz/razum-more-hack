from django.contrib import admin

from events.models import Event, EventCategory, Participation, Prize


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "organizer", "category", "event_date", "status")
    list_filter = ("status", "event_type", "category")
    search_fields = ("name", "description")


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "prize_type", "quantity")
    list_filter = ("prize_type",)


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "status", "points_awarded", "created_at")
    list_filter = ("status",)
    search_fields = ("event__name", "user__username", "user__email")
