from rest_framework.authtoken.views import ObtainAuthToken as BaseObtainAuthToken
from ..serializers import AuthTokenSerializer


class ObtainAuthToken(BaseObtainAuthToken):
    """obtain user auth token endpoint."""

    serializer_class = AuthTokenSerializer
