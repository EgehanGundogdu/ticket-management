from django.urls import path
from users.api import views  # noqa
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = "accounts"
urlpatterns = [
    path("token/obtain/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("register/", views.RegisterCompanyAdmin.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/", views.ActivateAccount.as_view(), name="activate"
    ),
]
