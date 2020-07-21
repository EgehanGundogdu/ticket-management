"invitation token handler."
import random

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

from hashids import Hashids


class InvitationsTokenHandler(Hashids):
    def encode_token(self, company_id, department_id=None):
        """
        returned min 25 character token. example (1,2) return o5ZpBQ8J0yelYfoaER7OYMzWx
        params
        :company id. -> the unique key of the company to which the user is invited.
        :department id. -> the unique key of the company department to which the user is invited.
        """
        if department_id is not None:
            return self.encode(company_id, department_id)
        return self.encode(company_id)

    def decode_token(self, token):
        """
        Returns decoded token.
        """
        return self.decode(token)


inviation_token_manager = InvitationsTokenHandler(settings.SECRET_KEY, min_length=25)


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


account_activate_token_handler = TokenGenerator()
