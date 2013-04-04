from django.db.models.signals import post_save
from django.dispatch import receiver
from open_municipio.acts.models import Act

@receiver(post_save, sender=Act)
def post_save_act_handler(sender, **kwargs):
    """
    This handler sends a mail to admins when an Act has been imported.
    """
    pass