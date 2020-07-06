"users app config file."
from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        "import signals when the app is ready."
        import users.signals
