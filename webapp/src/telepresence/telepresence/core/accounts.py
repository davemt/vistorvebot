import ldap
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class ActiveDirectoryGroupMembershipBackend(ModelBackend):
    def authenticate(self,username=None,password=None):
        try:
            if len(password) == 0:
                return None
            l = ldap.initialize(settings.AD_LDAP_URL)
            l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            binddn = "%s@%s" % (username,settings.AD_NT4_DOMAIN)
            l.simple_bind_s(binddn,password)
            l.unbind_s()
            return self.get_or_create_user(username)
        except ldap.INVALID_CREDENTIALS:
            pass

    def get_or_create_user(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username,first_name=username)
            user.is_staff = False
            user.is_superuser = False
            user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
