from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Profile


@receiver(user_signed_up)
def create_profile_on_signup(request, user, **kwargs):
    # Пытаемся достать данные из GitHub (через SocialAccount)
    social = user.socialaccount_set.filter(provider='github').first()
    login = social.extra_data.get('login') if social else None

    Profile.objects.get_or_create(
        user=user,
        defaults={'github_username': login}
    )