"""registration api view for users application."""
from rest_framework import generics, response
from .. import serializers, models
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from ..utils import send_confirmation_email_user


class RegisterCompanyAdmin(generics.CreateAPIView):
    """
    Registration api view for company admins.
    """

    serializer_class = serializers.StaffUserRegisterSerializer

    def create(self, request, *args, **kwargs):
        """call createapiviews create method and add custom message on response."""
        response = super().create(request, *args, **kwargs)
        response.data["message"] = "Check your email and activate your account."
        return response

    def perform_create(self, serializer):
        """save the serializer and send confirmation mail"""
        created = serializer.save()
        send_confirmation_email_user(self.request, created)
