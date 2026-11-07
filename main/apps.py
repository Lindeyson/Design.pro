from django.apps import AppConfig
from django.db.models.signals import post_migrate

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Design.pro'

    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)

def create_default_admin(sender, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@design.pro',
            password='admin',
            full_name='Администратор',
        )