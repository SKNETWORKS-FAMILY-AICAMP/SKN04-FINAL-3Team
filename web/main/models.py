from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        (0, 'Not Specified'),
        (1, 'Male'),
        (2, 'Female'),
    )

    country_id = models.CharField(max_length=50, null=True, blank=True, default="US")
    birthday = models.DateField(null=True, blank=True, default="2000-01-01")
    nickname = models.CharField(max_length=50, null=True, blank=True)
    thumbnail_id = models.IntegerField(null=True, blank=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)  # 선택 목록 추가

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set", 
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set_permissions",  
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta:
        db_table = 'main_customuser'  # 데이터베이스 테이블 이름
        managed = True


class Country(models.Model):
    country_id = models.CharField(max_length=50, primary_key=True)
    country_name = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'country'
        managed = True


class Settings(models.Model):
    profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.SET_DEFAULT, default="US")
    is_white_theme = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'settings'
        managed = True


class BookmarkPlace(models.Model):
    bookmarkplace_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=40)
    category = models.CharField(max_length=30, null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    overview = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarkplace'
        managed = True


class BookmarkSchedule(models.Model):
    bookmarkschedule_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)
    json_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarkschedule'
        managed = True
        

class Bookmark(models.Model):
    bookmark = models.CharField(max_length=50, primary_key=True)
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_place = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmark'
        managed = True


class BookmarkList(models.Model):
    bookmarkplace = models.ForeignKey(BookmarkPlace, on_delete=models.CASCADE, null=True, blank=True)
    bookmarkschedule = models.ForeignKey(BookmarkSchedule, on_delete=models.CASCADE, null=True, blank=True)
    bookmark = models.ForeignKey(Bookmark, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarklist'
        managed = True
        unique_together = [
            ('bookmark', 'bookmarkplace'),  # bookmark_id와 bookmarkplace_id 조합의 중복 방지
            ('bookmark', 'bookmarkschedule'),  # bookmark_id와 bookmarkschedule_id 조합의 중복 방지
        ]


class Chatting(models.Model):
    chatting_id = models.CharField(max_length=50, primary_key=True)
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    title = models.CharField(max_length=10, null=False, default="")  # 새로운 title 필드 추가
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.title:  # title이 비어있을 때만 기본값 생성
            # 현재 채팅 개수를 가져와 새로운 title 생성
            chat_count = Chatting.objects.filter(profile=self.profile).count()
            self.title = f"chat{chat_count + 1}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'chatting'
        managed = True