from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now


class CustomUser(AbstractUser):
    country_id = models.CharField(max_length=50, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    thumbnail_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)   

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # related_name 수정
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set_permissions",  # related_name 수정
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


class Country(models.Model):
    country_id = models.CharField(max_length=50, primary_key=True)
    country_name = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)  


class Settings(models.Model):
    profile_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE)
    is_white_theme = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  


class Place(models.Model):
    place_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    longitude = models.FloatField()
    latitude = models.FloatField()
    overview = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  

    class Meta:
        db_table = 'place'
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정


class Bookmark(models.Model):
    bookmark_id = models.CharField(max_length=50, primary_key=True)
    profile_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_place = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  


class BookmarkList(models.Model):
    place_id = models.ForeignKey(Place, on_delete=models.CASCADE)
    bookmark_id = models.ForeignKey(Bookmark, on_delete=models.CASCADE)
    day_num = models.IntegerField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  


class Chatting(models.Model):
    chatting_id = models.CharField(max_length=50, primary_key=True)
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  
