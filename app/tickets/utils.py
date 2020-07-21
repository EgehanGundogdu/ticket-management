from .models import Activity


def create_action(instance, verb, user):
    """create activity helper function."""
    return instance.activities.create(action=verb, owner=user)

