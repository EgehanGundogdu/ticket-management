from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, response, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api import serializers  # noqa
from ..token_handlers import account_activate_token_handler
from ..utils import send_confirmation_email_user


UserModel = get_user_model()


class ActivateAccount(APIView):
    """company official user registration confirmation"""

    def get(self, request, uidb64, token, *args, **kwargs):
        """decode token and uid and try to confirm registration."""
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (UserModel.DoesNotExist, TypeError, ValueError, OverflowError):
            user = None
        if user is not None and account_activate_token_handler.check_token(
            user=user, token=token
        ):
            user.is_active = True
            user.is_approved = True
            user.save()
            return Response(
                data={"message": "Your account activated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            data={"message": "Link is invalid. Try again"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RegisterCompanyAdmin(generics.CreateAPIView):
    """
    Registration api view for company admins.
    """

    serializer_class = serializers.CompanyAdminRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """call createapiviews create method and add custom message on response."""
        response = super().create(request, *args, **kwargs)
        response.data["message"] = "Check your email and activate your account."
        return response

    def perform_create(self, serializer):
        """save the serializer and send confirmation mail"""
        created = serializer.save()
        send_confirmation_email_user(self.request, created)
