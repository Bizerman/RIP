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
    path('gatewayel/<int:id>/addtomission/', views.GatewayelementstoDraft.as_view(), name='gateway-els-tomission'),
    path('gatewayel/<int:id>/image/', views.GatewayElementImageUpdate.as_view(), name='gateway-els-image'),
    path('gatewayel/<int:id>/', views.GatewayelementsDetail.as_view(), name='gateway-el-detail'),
    path('gatewayel/<int:id>/put/', views.put, name='gateway-el-put'),
    path('mission/<int:id>/', views.GatewayMissionDetail.as_view(), name='gateway-els-mission'),
    path('missions/', views.GatewayMissionList.as_view(), name='gateway-els-missions'),
    path('mission/<int:mission_id>/element/<int:element_id>/',views.GatewayElementMissionDetail.as_view(),name='gateway-el-mission-detail'),
    path('users/', views.UsersList.as_view(), name='users-list'),
    path('', include(router.urls)),
]
