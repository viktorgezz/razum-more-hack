from django.db import models


class PointWeight(models.Model):
    event_type = models.CharField(max_length=32)
    category = models.ForeignKey(
        "events.EventCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="point_weights",
    )
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    updated_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_point_weights",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("event_type", "category"),
                name="unique_event_type_category_weight",
            )
        ]
        ordering = ("event_type", "category_id")

    def __str__(self):
        category_slug = self.category.slug if self.category else "any"
        return f"{self.event_type}:{category_slug}={self.weight}"
