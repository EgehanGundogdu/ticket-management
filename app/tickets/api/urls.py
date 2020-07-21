from tickets.api.views import TicketViewSet
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()


app_name = "tickets"

router.register("", TicketViewSet)


urlpatterns = [path("", include(router.urls))]

