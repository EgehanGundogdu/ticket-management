"serializers of users application"
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password as auth_validate_password,
)

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
