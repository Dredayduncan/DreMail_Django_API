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
router.register(r'group/?', EmailGroupViewSet, basename="group")
router.register(r'users/?', UserViewSet, basename="users")
router.register(r'emailTransfers/?', EmailTransferViewSet, basename="emailTransfers")

urlpatterns = [
    path('', include(router.urls)),
    path('authenticate/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterUserView.as_view(), name="register"),
    re_path('change_password/', ChangePasswordView.as_view(), name='change_password'),
]