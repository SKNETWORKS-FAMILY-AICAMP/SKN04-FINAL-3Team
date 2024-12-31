from django.db import models
from django.contrib.auth.models import User

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # auth_user와 연결
#     birthday = models.DateField(null=True, blank=True)
#     password = models.CharField(max_length=255, editable=False)
#     nickname = models.CharField(max_length=50, unique=True, null=True, blank=True)
#     user_iid = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_iid_set')  # 외래 키 설정
#     nation_id = models.CharField(max_length=50, null=True, blank=True)

#     def __str__(self):
#         return self.user.username
