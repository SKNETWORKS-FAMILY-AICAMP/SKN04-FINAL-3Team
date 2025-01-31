from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         # UserProfile 생성
#         UserProfile.objects.create(
#             user=instance,
#             user_iid=instance,  # user_iid에 auth_user의 객체 저장
#             password=instance.password
#         )
