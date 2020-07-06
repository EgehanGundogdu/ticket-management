from django.core.mail import send_mail
from django.template.loader import render_to_string
from .token_handlers import account_activate_token_handler
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.conf import settings


def uid_token_generator(instance) -> dict:
    """
    Creater util function of uid and token for user.
    """
    return {
        "uidb64": urlsafe_base64_encode(force_bytes(instance.id)),
        "token": account_activate_token_handler.make_token(instance),
    }


def send_confirmation_email_user(request, instance) -> bool:
    """
    When the company representative is registered, 
    sending an e-mail to activate his account
    """
    recipent = request.user
    mail_subject = "Activate your account. Before login."
    current_site = get_current_site(request)
    uid_token = uid_token_generator(instance)
    message = render_to_string(
        "users/activate_account.html",
        {"user": instance, "domain": current_site.domain, **uid_token},
    )
    email = send_mail(
        mail_subject,
        message,
        settings.EMAIL_HOST_USER,
        (instance.email,),
        fail_silently=True,
    )
    return email
