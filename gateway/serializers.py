from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from gateway.models import Gateway_el, Gateway_mission, gateway_element_and_mission, AuthUser


class GatewayElementSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Gateway_el
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    element_set = GatewayElementSerializer(many=True, read_only=True)

    class Meta:
        model = AuthUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        user = AuthUser.objects.create(**validated_data)
        return user
class GatewayElementMissionSerializer(serializers.ModelSerializer):
    element = GatewayElementSerializer(read_only=True)
    class Meta:
        model = gateway_element_and_mission
        fields = ['element_id','mission_id']
class GatewayMissionSerializer(serializers.ModelSerializer):
    elements = GatewayElementMissionSerializer(
        source='mission_elements',
        many=True,
        read_only=True
    )
    class Meta:
        model = Gateway_mission
        fields = ['id', 'status', 'create_datetime', 'form_datetime',
                  'complete_datetime', 'moderator', 'creator','elements']

