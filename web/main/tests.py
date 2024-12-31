# from django.test import TestCase
# from django.contrib.auth.models import User
# from main.models import UserProfile

# class UserProfileTestCase(TestCase):
#     def test_user_profile_creation(self):
#         # 새로운 사용자 생성
#         new_user = User.objects.create_user(username="testuser", password="password123")

#         # UserProfile 확인
#         user_profile = UserProfile.objects.get(user=new_user)

#         # user_iid가 올바르게 설정되었는지 확인
#         self.assertEqual(user_profile.user_iid.id, new_user.id)
#         self.assertEqual(user_profile.user.username, "testuser")
