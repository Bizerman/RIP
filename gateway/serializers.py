from django.contrib.auth.models import User
from rest_framework import serializers
from gateway.models import Gateway_el, Gateway_mission


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class GatewayElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway_el
        fields = '__all__'
class GatewayMisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway_mission
        fields = '__all__'

