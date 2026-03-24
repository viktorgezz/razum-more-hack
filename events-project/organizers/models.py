from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class OrganizerReview(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='written_reviews',
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='organizer_reviews',
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв об организаторе'
        verbose_name_plural = 'Отзывы об организаторах'
        unique_together = ('reviewer', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reviewer} -> {self.organizer} ({self.score})'
