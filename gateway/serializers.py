
from rest_framework import serializers
from gateway.models import Gateway_el, Gateway_mission, gateway_element_and_mission, AuthUser


class GatewayElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway_el
        fields = ['id','title','short_description','status','img_url','full_description']



class GatewayElementWithoutImg(serializers.ModelSerializer):
    class Meta:
        model = Gateway_el
        fields = ['id','title','short_description','status','full_description']


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = AuthUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['email', 'password']


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = AuthUser
        fields = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active']


class GatewayElementMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = gateway_element_and_mission
        fields = ['element_id','mission_id']
class GatewayAdditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = gateway_element_and_mission
        fields = ['addition']

class GatewayMissionSerializer(serializers.ModelSerializer):
    elements = GatewayElementMissionSerializer(
        source='mission_elements',
        many=True,
        read_only=True
    )
    class Meta:
        model = Gateway_mission
        fields = ['id','mission_name','plan_date', 'status', 'create_datetime', 'form_datetime',
                  'complete_datetime', 'moderator', 'creator','addition','elements']

    def to_representation(self, mission):
        text_mission_status = super().to_representation(mission)
        if mission.status is not None:
            text_mission_status['status'] = mission.get_status_display()
        return text_mission_status
class GatewayMissionAdditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway_mission
        fields = ['mission_name','addition']