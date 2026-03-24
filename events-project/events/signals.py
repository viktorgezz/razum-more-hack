from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import Participation


@receiver(post_save, sender=Participation)
def participation_confirmed_handler(sender, instance: Participation, created, **kwargs):
    # Hook for ratings recalculation integration on confirmation.
    if created:
        return
    if instance.status == Participation.Status.CONFIRMED:
        return
