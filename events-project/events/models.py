from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.utils import timezone


class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Категория мероприятия'
        verbose_name_plural = 'Категории мероприятий'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Event(models.Model):
    class EventType(models.TextChoices):
        LECTURE = 'LECTURE', 'Лекция'
        HACKATHON = 'HACKATHON', 'Хакатон'
        FORUM = 'FORUM', 'Форум'
        VOLUNTEER = 'VOLUNTEER', 'Волонтёрство'
        OTHER = 'OTHER', 'Другое'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Черновик'
        PUBLISHED = 'PUBLISHED', 'Опубликовано'
        ONGOING = 'ONGOING', 'Идёт'
        COMPLETED = 'COMPLETED', 'Завершено'
        CANCELLED = 'CANCELLED', 'Отменено'

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events'
    )
    category = models.ForeignKey(
        EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField()
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    difficulty_coef = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
    base_points = models.PositiveIntegerField(default=10)
    max_participants = models.PositiveIntegerField(default=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ('-event_date',)

    def __str__(self):
        return self.name

    def calculate_points(self) -> int:
        value = Decimal(self.base_points) * Decimal(str(self.difficulty_coef))
        return int(value.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


class Prize(models.Model):
    class PrizeType(models.TextChoices):
        MERCH = 'MERCH', 'Мерч'
        TICKETS = 'TICKETS', 'Билеты'
        INTERNSHIP = 'INTERNSHIP', 'Стажировка'
        GRANT = 'GRANT', 'Грант'
        MEETING = 'MEETING', 'Встреча'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='prizes')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prize_type = models.CharField(max_length=20, choices=PrizeType.choices)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Приз'
        verbose_name_plural = 'Призы'

    def __str__(self):
        return self.name


class Participation(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'REGISTERED', 'Зарегистрирован'
        CHECKED_IN = 'CHECKED_IN', 'Отмечен'
        CONFIRMED = 'CONFIRMED', 'Подтверждён'
        REJECTED = 'REJECTED', 'Отклонён'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REGISTERED)
    qr_token = models.CharField(max_length=255, unique=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    points_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Участие'
        verbose_name_plural = 'Участия'
        unique_together = ('event', 'user')

    def __str__(self):
        return f'{self.user} - {self.event}'

    def mark_checked_in(self):
        self.status = self.Status.CHECKED_IN
        self.checked_in_at = timezone.now()

    def mark_confirmed(self):
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
