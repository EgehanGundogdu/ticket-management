from rest_framework import serializers
from tickets.models import Ticket
from companies.models import Company, Department
from django.contrib.auth import get_user_model


User = get_user_model()


class NormalUserTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("header", "content", "department", "company", "id")
        read_only_fields = ("identifier", "id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        self.fields["company"].queryset = Company.objects.filter(customers__id=user.id)
        self.fields["department"].queryset = Department.objects.filter(
            company__customers__id=user.id
        )


class CompanyAdminTicketSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ticket
        exclude = [
            "identifier",
        ]
        read_only_fields = ("id",)

    def get_owner(self, instance):
        return instance.owner.get_full_name()

