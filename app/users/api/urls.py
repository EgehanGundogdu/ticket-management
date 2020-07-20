from django.urls import path
from users.api import views  # noqa


app_name = "accounts"
urlpatterns = [
    path("register/", views.RegisterCompanyAdmin.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/", views.ActivateAccount.as_view(), name="activate"
    ),
]
