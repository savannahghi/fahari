from unittest.mock import MagicMock

from pepfar_mle.users.adapters import AccountAdapter, SocialAccountAdapter


class TestAdapters:
    def test_is_open_for_signup(self):

        req = MagicMock()
        social_login = MagicMock()

        account_adapter = AccountAdapter()
        assert account_adapter.is_open_for_signup(request=req) is True

        social_adapter = SocialAccountAdapter()
        assert social_adapter.is_open_for_signup(request=req, sociallogin=social_login) is True
