"""aiscratch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken import views
from rest_framework import routers
from production.views import RegistrationViewSet, UserDetailViewSet, ProductionViewSet, Sb3Snap, Sb3Path, DownModelFile, ChatRobot, AudioRecognaztion 

router = routers.DefaultRouter()
router.register(r'registration', RegistrationViewSet)
router.register(r'userdetail', UserDetailViewSet)
router.register(r'production', ProductionViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'api-auth/', include('rest_framework.urls')),
    url(r'api/', include(router.urls)),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^sb3file/(?P<puuid>.*)', Sb3Path.as_view()),
    url(r'^sb3snap/(?P<puuid>.*)', Sb3Snap.as_view()),
    url(r'^00000000-0000-0000-0000-000000015000/model/(?P<modelfile>.*)', DownModelFile.as_view()),
    url(r'^00000000-0000-0000-0000-000000015000/chat_robot', ChatRobot.as_view()),
    url(r'^00000000-0000-0000-0000-000000015000/audio_recognize', AudioRecognaztion.as_view()),
]
