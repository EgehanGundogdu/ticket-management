from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from ..token_handlers import account_activate_token_handler
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

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
