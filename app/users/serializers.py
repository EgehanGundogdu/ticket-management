"serializers of users application"
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import (
    validate_password as auth_validate_password,
)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import (
    AuthTokenSerializer as BaseAuthTokenSerializer,
)

from .models import StaffInvitation

UserModel = get_user_model()


class StaffUserRegisterSerializer(serializers.ModelSerializer):
    """serializes company admin register fields.
    uses for only registration
    """

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}, max_length=255
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}, max_length=255
    )

    class Meta:
        model = UserModel
        fields = ["first_name", "last_name", "email", "password", "password2", "id"]
        read_only_fields = ("id",)

    def validate(self, attrs):
        """check password equality."""
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError("Password fields does not match")
        return attrs

    def validate_password(self, value):
        """validate password value with builtin django auth password validators."""
        auth_validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        """create new company admin user with validated data."""
        validated_data.pop("password2")
        return UserModel.objects.create_company_admin(**validated_data)


class AuthTokenSerializer(BaseAuthTokenSerializer):
    """obtain auth token serializer"""

    username = None
    email = serializers.EmailField(label=_("email"))

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class StaffInvitationSerializer(serializers.ModelSerializer):
    "serializes to staff invitation instances."

    class Meta:
        "meta class definition for staffinvitatitonserializer."
        model = StaffInvitation
        fields = ["first_name", "last_name", "email", "confirmed", "created"]
        read_only_fields = ["confirmed", "created"]

    def validate_email(self, value):
        """check email exist in user model or invitation models 
            email must be unique for user model."""
        if (
            UserModel.objects.filter(email=value).exists()
            or StaffInvitation.objects.filter(email=value).exists()
        ):
            raise serializers.ValidationError(
                _("a registered user or previously invited this e-mail address.")
            )

        return value
