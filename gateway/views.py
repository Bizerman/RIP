from rest_framework.response import Response
from rest_framework.views import APIView

from gateway.models import Gateway_el
from gateway.serializers import GatewayElementSerializer


class GatewayelementsList(APIView):
    model_class = Gateway_el
    serializer_class = GatewayElementSerializer
    def get(self, request, format=None):
        gateway_elements = self.model_class.objects.all()
        serializer = self.serializer_class(gateway_elements, many=True)
        return Response(serializer.data)


