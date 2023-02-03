from django.urls import path, include
from dre_mail_api.views import *

urlpatterns = [
    path('users/', EmailUserView.as_view()),
    path('users/<int:userID>/', EmailUserDetailView.as_view())
]