from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import Participation
from rating.services import rebuild_leaderboard, update_user_snapshot


@receiver(post_save, sender=Participation)
def on_participation_confirmed(sender, instance, **kwargs):
    if instance.status == 'CONFIRMED':
        update_user_snapshot(instance.user_id)
        rebuild_leaderboard()
