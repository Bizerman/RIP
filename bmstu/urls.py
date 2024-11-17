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
    path('', include(router.urls)),
    path(r'gatewayels_list/', views.GatewayelementsList.as_view(), name='gateway-els-list'),
    # path('gateway_element/<int:id>/', views.gateway_product_page_render, name='gateway_el_url'),
    # path('gateway_mission/<int:id>/', views.mission_page_render, name='gateway_mission_url'),
    # path('gateway_mission/<int:id>/delete/', views.del_mission, name="delete_mission"),
    # path('gateway_el/<int:el_id>/add_to_mission/', views.add_to_mission, name='el_add_to_mission')
]
