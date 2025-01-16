# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin  # UserAdmin import
# from django.contrib.auth.models import User  # User 모델 import
# from .models import UserProfile  # UserProfile 모델 import


# # UserProfileInline 정의를 CustomUserAdmin보다 위로 이동
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     fk_name = 'user'  # user 필드를 외래 키로 지정

# class CustomUserAdmin(UserAdmin):
#     inlines = (UserProfileInline,)

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         # UserProfile이 없는 경우에만 생성
#         if not UserProfile.objects.filter(user=obj).exists():
#             UserProfile.objects.create(
#                 user=obj,
#                 user_iid=obj,  # user_id 값을 user_iid에 매핑
#                 password=obj.password
#             )

# # 기존 UserAdmin을 CustomUserAdmin으로 대체
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
