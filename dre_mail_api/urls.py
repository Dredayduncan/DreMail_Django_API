from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from dre_mail_api.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter(trailing_slash=False)
router.register('emails/', EmailViewSet, basename="email")
router.register(r'drafts/?', DraftViewSet, basename="drafts")

urlpatterns = [
    path('', include(router.urls)),
    path('authenticate/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterUserView.as_view(), name="register"),
    re_path(r'^change_password/(?P<userID>\d+)?/?$', ChangePasswordView.as_view(), name='change_password'),
    re_path(r'^update_profile/(?P<userID>\d+)?/?$', UpdateProfileView.as_view(), name='update_profile'),
    re_path(r'^update_avi/(?P<userID>\d+)?/?$', UpdateAVIView.as_view(), name='update_avi'),
    path('users/', UserView.as_view()),
    re_path(r'^user/(?P<userID>\d+)?/?$', UserDetailView.as_view(), name="userDetail"),
]