from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi

from gateway import views

router = DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gatewayels_list/', views.GatewayElementsList.as_view(), name='gateway-els-list'),
    path('gatewayel/<int:id>/addtomission/', views.add_element_to_draft, name='gateway-els-tomission'),
    path('gatewayel/<int:id>/image/', views.gateway_element_img_update, name='gateway-els-image'),
    path('gatewayel/<int:id>/', views.GatewayElementsDetail.as_view(), name='gateway-el-detail'),
    path('gatewayel/<int:id>/put/', views.gateway_element_update, name='gateway-el-put'),
    path('mission/<int:id>/', views.GatewayMissionDetail.as_view(), name='gateway-els-mission'),
    path('mission/form/', views.gateway_mission_form, name='gateway-creator-form'),
    path('mission/<int:id>/complete/', views.gateway_mission_complete, name='gateway-moderator-form'),
    path('missions/', views.gateway_missions_list, name='gateway-els-missions'),
    path('mission/<int:mission_id>/element/<int:element_id>/', views.GatewayElementMissionDetail.as_view(), name='gateway-el-mission'),
    path('user/registration/', views.register, name='user-registration'),
    path('user/<int:id>/change_profile/', views.ChangeProfile, name='user-change-profile'),
    path('user/login/', views.login_view, name='user-login'),
    path('user/logout/', views.logout_view, name='user-logout'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
