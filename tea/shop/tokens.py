from django.contrib.auth.tokens import PasswordResetTokenGenerator

class CustomerTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # The default generator looks for user.last_login which Customer doesn't have.
        # So we override it to only use pk, password, and timestamp.
        return str(user.pk) + str(user.password) + str(timestamp)

token_generator = CustomerTokenGenerator()