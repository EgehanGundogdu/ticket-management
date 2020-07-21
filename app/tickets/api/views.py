from rest_framework import viewsets, permissions
from tickets.models import Ticket
from tickets.api.serializers import (
    NormalUserTicketSerializer,
    CompanyAdminTicketSerializer,
)
from django.db.models import Q
from tickets.api.permissions import TicketUserTypePermission


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = NormalUserTicketSerializer
    permission_classes = (permissions.IsAuthenticated, TicketUserTypePermission)
    lookup_field = "identifier"
    lookup_url_kwarg = "identifier"

    def get_queryset(self):
        user = self.request.user
        if user.is_company_admin:
            return self.queryset.filter(Q(company__leader=user))
        elif user.is_staff:
            return self.queryset.filter(Q(department__members__id=user.id))
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.user.is_company_admin or self.request.user.is_staff:
            return CompanyAdminTicketSerializer
        return NormalUserTicketSerializer

