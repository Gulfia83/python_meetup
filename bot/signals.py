from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Letters

@receiver(post_save, sender=Letters)
def send_newsletter_on_save(sender, instance, created, **kwargs):
    print("wegfwrgwrg")
    if created and instance.sent_at is None:
        instance.send_to_all_users()
