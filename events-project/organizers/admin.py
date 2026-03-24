from django.contrib import admin

from .models import OrganizerReview


@admin.register(OrganizerReview)
class OrganizerReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'organizer', 'event', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('reviewer__username', 'organizer__username', 'event__name')
