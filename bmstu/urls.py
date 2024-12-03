"""
URL configuration for bmstu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from gateway import views

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gatewayels_list/', views.GatewayelementsList.as_view(), name='gateway-els-list'),
    path('gatewayel/<int:id>/addtomission/', views.add_element_to_draft, name='gateway-els-tomission'),
    path('gatewayel/<int:id>/image/', views.gateway_element_img_update, name='gateway-els-image'),
    path('gatewayel/<int:id>/', views.GatewayelementsDetail.as_view(), name='gateway-el-detail'),
    path('gatewayel/<int:id>/put/', views.gateway_element_update, name='gateway-el-put'),
    path('mission/<int:id>/', views.GatewayMissionDetail.as_view(), name='gateway-els-mission'),
    path('mission/<int:id>/form/', views.gateway_mission_form, name='gateway-creator-form'),
    path('mission/<int:id>/complete/', views.gateway_mission_complete, name='gateway-moderator-form'),
    path('missions/', views.gateway_missions_list, name='gateway-els-missions'),
    path('mission/<int:mission_id>/element/<int:element_id>/',views.GatewayElementMissionDetail.as_view(),name='gateway-el-mission'),
    path('user/registration/', views.Registration, name='user-registration'),
    path('user/<int:id>/change_profile/', views.ChangeProfile, name='user-change-profile'),
    path('user/authentication/', views.Authentication, name='user-authentication'),
    path('user/<int:id>/deathtorization/', views.Deathtorization, name='user-deathtorization'),
    path('', include(router.urls)),
]
