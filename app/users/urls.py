from django.urls import path
from users import api


app_name = "accounts"
urlpatterns = [
    path("register/", api.RegisterCompanyAdmin.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", api.ActivateAccount.as_view(), name="activate"),
    path("obtain-token/", api.ObtainAuthToken.as_view(), name="obtain-token"),
]

