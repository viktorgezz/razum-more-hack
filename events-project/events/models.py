from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.utils import timezone


class EventCategory(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Event(models.Model):
    class EventType(models.TextChoices):
        LECTURE = "LECTURE", "Lecture"
        HACKATHON = "HACKATHON", "Hackathon"
        FORUM = "FORUM", "Forum"
        VOLUNTEER = "VOLUNTEER", "Volunteer"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ONGOING = "ONGOING", "Ongoing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organized_events"
    )
    category = models.ForeignKey(
        EventCategory, on_delete=models.PROTECT, related_name="events"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    difficulty_coef = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("1.00"))
    base_points = models.PositiveIntegerField(default=0)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ("-event_date",)

    def __str__(self):
        return self.name

    def calculate_points(self) -> int:
        value = Decimal(self.base_points) * Decimal(str(self.difficulty_coef))
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class Prize(models.Model):
    class PrizeType(models.TextChoices):
        MERCH = "MERCH", "Merch"
        TICKETS = "TICKETS", "Tickets"
        INTERNSHIP = "INTERNSHIP", "Internship"
        GRANT = "GRANT", "Grant"
        MEETING = "MEETING", "Meeting"

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="prizes")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    prize_type = models.CharField(max_length=20, choices=PrizeType.choices)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.event.name})"


class Participation(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Registered"
        CHECKED_IN = "CHECKED_IN", "Checked In"
        CONFIRMED = "CONFIRMED", "Confirmed"
        REJECTED = "REJECTED", "Rejected"

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participations")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_participations"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REGISTERED)
    qr_token = models.CharField(max_length=128, unique=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    points_awarded = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("event", "user"), name="unique_event_user_participation")
        ]

    def __str__(self):
        return f"{self.user} - {self.event}"

    def mark_checked_in(self):
        self.status = self.Status.CHECKED_IN
        self.checked_in_at = timezone.now()

    def mark_confirmed(self):
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
