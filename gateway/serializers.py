from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from gateway.models import Gateway_el, Gateway_mission, gateway_element_and_mission, AuthUser


class GatewayElementSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Gateway_el
        fields = '__all__'

class GatewayElementWithoutImg(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Gateway_el
        fields = ['id','title','short_description','status','full_description','user']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username','password']
class GatewayElementMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = gateway_element_and_mission
        fields = ['element_id','mission_id']
class GatewayElementTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = gateway_element_and_mission
        fields = ['element_type']  # Добавляем только необходимые поля

    def to_representation(self, m_m):
        text_element_type = super().to_representation(m_m)
        if m_m.element_type is not None:
            text_element_type['element_type'] = m_m.get_element_type_display()
        return text_element_type
class GatewayMissionSerializer(serializers.ModelSerializer):
    elements = GatewayElementMissionSerializer(
        source='mission_elements',
        many=True,
        read_only=True
    )
    class Meta:
        model = Gateway_mission
        fields = ['id','mission_name','plan_date', 'status', 'create_datetime', 'form_datetime',
                  'complete_datetime', 'moderator', 'creator','elements']

    def to_representation(self, mission_status):
        text_mission_status = super().to_representation(mission_status)
        if mission_status.element_type is not None:
            text_mission_status['element_type'] = mission_status.get_element_type_display()
        return text_mission_status
class GatewayMissionAdditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway_mission
        fields = ['mission_name','plan_date']