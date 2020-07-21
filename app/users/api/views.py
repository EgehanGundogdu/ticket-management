from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, response, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from users.api import serializers  # noqa
from users.api.permissions import CompanyAdmin
from ..token_handlers import account_activate_token_handler, inviation_token_manager
from ..utils import send_confirmation_email_user
from users.models import Invitation
from companies.models import Company, Department

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


from ..utils import send_invitation_confirm_email


class CompanyStaffEmployeeInvite(generics.ListCreateAPIView):
    serializer_class = serializers.CompanyStaffInviteSerializer
    permission_classes = (permissions.IsAuthenticated, CompanyAdmin)
    queryset = Invitation.objects.all()

    def get_queryset(self):
        return self.queryset.filter(inviter=self.request.user)

    def perform_create(self, serializer):
        inviter = self.request.user
        invited = serializer.save(inviter=inviter)
        send_invitation_confirm_email(self.request, invited)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status.HTTP_201_CREATED, headers=headers)


from ..utils import get_random_alphanumeric_string

User = get_user_model()


class InviteConfirm(APIView):
    def get(self, request, uuid, *args, **kwargs):
        try:
            invite = Invitation.objects.get(uuid=uuid, confirmed=False)
            decoded_token = inviation_token_manager.decode_token(invite.token)
        except Invitation.DoesNotExist:
            return Response({"error": {"Invalid uuid"}}, status.HTTP_400_BAD_REQUEST)
        generate_random_password = get_random_alphanumeric_string(7, 6)
        if len(decoded_token) == 2:
            user = User.objects.create_user(
                first_name=invite.first_name,
                last_name=invite.last_name,
                email=invite.email,
                password=generate_random_password,
                is_active=True,
                is_staff=True,
            )
            company = Company.objects.get(id=decoded_token[0])
            department = Department.objects.get(id=decoded_token[1])
            company.employees.add(user)
            department.members.add(user)
        else:
            user = User.objects.create_user(
                first_name=invite.first_name,
                last_name=invite.last_name,
                email=invite.email,
                is_staff=False,
                password=generate_random_password,
                is_active=True,
            )
            company = Company.objects.get(id=decoded_token[0])
            company.customers.add(user)
        invite.confirmed = True
        invite.save()
        return Response(
            {"success": "Invitation verified completed."}, status=status.HTTP_200_OK
        )
