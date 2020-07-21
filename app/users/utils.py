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


import random
import string


def get_random_alphanumeric_string(letters_count, digits_count):
    sample_str = "".join(
        (random.choice(string.ascii_letters) for i in range(letters_count))
    )
    sample_str += "".join((random.choice(string.digits) for i in range(digits_count)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = "".join(sample_list)
    return final_string


def send_invitation_confirm_email(request, invited) -> bool:
    """
    When the company representative is registered, 
    sending an e-mail to activate his account
    """
    mail_subject = "Confirm your invitation."
    current_site = get_current_site(request)

    if isinstance(invited, list):
        for i in invited:
            message = render_to_string(
                "users/confirm_invitation.html",
                {"invited": i, "domain": current_site.domain,},
            )
            email = send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                (i.email,),
                fail_silently=True,
            )
            return email
    else:
        message = render_to_string(
            "users/confirm_invitation.html",
            {"invited": invited, "domain": current_site.domain,},
        )
        return send_mail(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            (invited,),
            fail_silently=True,
        )

