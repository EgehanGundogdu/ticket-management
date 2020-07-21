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
from users.models import Invitation
from companies.models import Company, Department

UserModel = get_user_model()


class CompanyAdminRegistrationSerializer(serializers.ModelSerializer):
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


from ..token_handlers import inviation_token_manager
from ..utils import send_invitation_confirm_email


class CompanyStaffInviteSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), write_only=True
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Invitation
        exclude = ("inviter",)
        read_only_fields = ("id", "confirmed", "inviter", "uuid")

    def create(self, validated_data):
        if validated_data.get("department") is None:
            token = inviation_token_manager.encode_token(validated_data["company"].id)
            validated_data.pop("company")
        else:
            token = inviation_token_manager.encode_token(
                validated_data["company"].id, validated_data["department"].id
            )
            validated_data.pop("company")
            validated_data.pop("department")
        validated_data["token"] = token
        instance = super().create(validated_data)

        # send_invitation_confirm_email(
        #     request=self.context.get("request"), invited=instance
        # )
        return instance

