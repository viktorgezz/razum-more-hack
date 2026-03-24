from django.conf import settings
from django.db import models


class RatingSnapshot(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rating_snapshots',
    )
    rating_it = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating_social = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating_media = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    common_rating = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rank = models.PositiveIntegerField(default=0)
    snapshot_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Снимок рейтинга'
        verbose_name_plural = 'Снимки рейтинга'
        ordering = ['rank']

    def __str__(self):
        return f'{self.user} - rank {self.rank}'


class PointWeight(models.Model):
    class EventType(models.TextChoices):
        LECTURE = 'LECTURE', 'Лекция'
        HACKATHON = 'HACKATHON', 'Хакатон'
        FORUM = 'FORUM', 'Форум'
        VOLUNTEER = 'VOLUNTEER', 'Волонтёрство'

    event_type = models.CharField(max_length=50, choices=EventType.choices)
    category = models.ForeignKey(
        'events.EventCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Вес баллов'
        verbose_name_plural = 'Веса баллов'
        unique_together = ('event_type', 'category')

    def __str__(self):
        return f'{self.get_event_type_display()} / {self.category or "-"} x {self.weight}'
