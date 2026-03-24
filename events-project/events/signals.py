from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Participation


@receiver(pre_save, sender=Participation)
def trigger_rating_recalculation_on_confirm(sender, instance: Participation, **kwargs):
    if not instance.pk:
        return

    previous = sender.objects.filter(pk=instance.pk).only("status").first()
    if not previous:
        return

    if previous.status == Participation.Status.CONFIRMED:
        return

    if instance.status == Participation.Status.CONFIRMED:
        try:
            from rating.services import recalculate_user_rating
        except Exception:
            return
        recalculate_user_rating(user_id=instance.user_id)
