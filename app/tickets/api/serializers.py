from rest_framework import serializers
from tickets.models import Ticket
from companies.models import Company, Department
from django.contrib.auth import get_user_model


User = get_user_model()


class NormalUserTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("header", "content", "department", "company", "id", "owner")
        read_only_fields = ("identifier", "id", "owner")

    # def __init__(self, *args, **kwargs):
    #     super().__init__(self, *args, **kwargs)
    #     user = self.context["request"].user
    #     self.fields["company"].queryset = Company.objects.filter(customers__in=user)


class CompanyAdminTicketSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"

    def get_owner(self, instance):
        return instance.owner.get_full_name()

