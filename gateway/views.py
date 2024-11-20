from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from gateway.minio import add_img
from gateway.models import Gateway_el, AuthUser, Gateway_mission, gateway_element_and_mission
from gateway.serializers import GatewayElementSerializer, UserSerializer, GatewayMissionSerializer, \
    GatewayElementMissionSerializer


def user():
    try:
        user1 = AuthUser.objects.get(id=1)
    except:
        user1 = AuthUser(id=1, first_name="Иван", last_name="Иванов", password=1234, username="user1")
        user1.save()
    return user1


class GatewayelementsList(APIView):
    model_class = Gateway_el
    serializer_class = GatewayElementSerializer
    def get(self, request, format=None):
        user1 = user()
        gateway_elements = self.model_class.objects.filter(user=user1)
        draft_mission = Gateway_mission.objects.filter(status=1).first()
        if draft_mission is None:
            draft_mission = Gateway_mission.objects.create()
            draft_mission.creator = user1
            draft_mission.create_datetime = timezone.now()
            draft_mission.save()
        if not gateway_element_and_mission.objects.filter(mission=draft_mission).exists():
            items_to_create = [
                gateway_element_and_mission(mission=draft_mission, element=element)
                for element in self.model_class.objects.filter(user=user1)
            ]
            gateway_element_and_mission.objects.bulk_create(items_to_create)

        element_count = gateway_element_and_mission.objects.filter(mission=draft_mission).count()
        response_data = {
            "elements": self.serializer_class(gateway_elements, many=True).data,
            "draft_mission_id": draft_mission.id,
            "draft_element_count": element_count,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user1 = user()
            gateway_element = serializer.save(user=user1)
            return Response(self.serializer_class(gateway_element).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GatewayelementstoDraft(APIView):
    model_class = Gateway_el
    serializer_class = GatewayElementSerializer

    def post(self, request, id, format=None):
        user1 = user()
        draft_mission = Gateway_mission.objects.filter(status=1).first()
        if draft_mission is None:
            draft_mission = Gateway_mission.objects.create()
            draft_mission.creator = user1
            draft_mission.create_datetime = timezone.now()
            draft_mission.save()

        element = get_object_or_404(Gateway_el, id=id)
        if gateway_element_and_mission.objects.filter(mission=draft_mission, element=element).exists():
            return Response(
                {"error": "Элемент уже добавлен в черновик"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        gateway_element_and_mission.objects.create(mission=draft_mission, element=element)

        return Response({"mission_id": draft_mission.id},status=status.HTTP_201_CREATED)


class GatewayElementImageUpdate(APIView):
    model_class = Gateway_el
    serializer_class = GatewayElementSerializer

    def post(self, request, id, format=None):
        gateway_element = get_object_or_404(Gateway_el, id=id)
        new_image = request.FILES.get("img")

        if not new_image:
            return Response({"error": "Изображение не предоставлено"}, status=status.HTTP_400_BAD_REQUEST)

        # Обработка изображения
        img_result = add_img(gateway_element, new_image)

        if isinstance(img_result, dict) and 'error' in img_result:
            return Response(img_result, status=status.HTTP_400_BAD_REQUEST)

        # Сериализация данных для ответа
        serialized_data = self.serializer_class(gateway_element).data
        return Response({"img_url": serialized_data.get('img_url')}, status=status.HTTP_200_OK)


class GatewayelementsDetail(APIView):
    model_class = Gateway_el
    serializer_class = GatewayElementSerializer

    def get(self, request, id, format=None):
        gateway_element = get_object_or_404(self.model_class, id=id)
        serializer = self.serializer_class(gateway_element)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        gateway_element = get_object_or_404(self.model_class, id=id)
        serializer = self.serializer_class(gateway_element, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        # Изменение фото логотипа
        if 'img' in serializer.initial_data:
            img_result = add_img(gateway_element, serializer.initial_data['img'])
            if isinstance(img_result, dict) and 'error' in img_result:
                return Response(img_result, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        gateway_element = get_object_or_404(self.model_class, id=id)
        gateway_element.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['Put'])
def put(self, request, id, format=None):
    gateway_element = get_object_or_404(self.model_class, id=id)
    serializer = self.serializer_class(gateway_element, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GatewayMissionList(APIView):
    model_class = Gateway_mission
    serializer_class = GatewayMissionSerializer

    def get(self, request, format=None):
        gateway_els = self.model_class.objects.exclude(status='5').exclude(status='1')

        # Фильтрация по статусу
        status_filter = request.query_params.get("status")
        if status_filter:
            gateway_els = gateway_els.filter(status=status_filter)

        # Фильтрация по диапазону даты формирования
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date or end_date:
            try:
                if start_date:
                    start_date = parse_datetime(start_date)
                    gateway_els = gateway_els.filter(form_datetime__gte=start_date)

                if end_date:
                    end_date = parse_datetime(end_date)
                    gateway_els = gateway_els.filter(form_datetime__lte=end_date)

            except ValueError:
                return Response(
                    {"error": "Неверный формат дат. Используйте формат YYYY-MM-DDTHH:MM:SS."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Сериализация данных
        serializer = self.serializer_class(gateway_els, many=True)
        data = serializer.data

        # Замена ID модератора и создателя на их логины
        for item in data:
            if item.get("moderator"):
                moderator = AuthUser.objects.filter(id=item["moderator"]).first()
                if moderator:
                    item["moderator"] = moderator.username

            if item.get("creator"):
                creator = AuthUser.objects.filter(id=item["creator"]).first()
                if creator:
                    item["creator"] = creator.username

        return Response(data, status=status.HTTP_200_OK)


class GatewayMissionDetail(APIView):
    model_class = Gateway_mission
    serializer_class = GatewayMissionSerializer
    def get(self, request, id, format=None):
        # Получаем миссию по ID
        gateway_mission = get_object_or_404(self.model_class, id=id)
        gateway_elements = gateway_element_and_mission.objects.filter(mission=gateway_mission)
        # Сериализуем элементы
        elements = [GatewayElementSerializer(entry.element).data for entry in gateway_elements]
        # Сериализуем миссию
        serializer = self.serializer_class(gateway_mission)
        data = serializer.data

        # Заменяем ID модератора и создателя на их логины
        if data.get("moderator"):
            moderator = AuthUser.objects.filter(id=data["moderator"]).first()
            if moderator:
                data["moderator"] = moderator.username

        if data.get("creator"):
            creator = AuthUser.objects.filter(id=data["creator"]).first()
            if creator:
                data["creator"] = creator.username
        response_data = {
            "mission": data,
            "elements": elements,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def put(self, request, id, format=None):
        gateway_mission = get_object_or_404(self.model_class, id=id)
        serializer = self.serializer_class(gateway_mission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id, format=None):
        gateway_mission = get_object_or_404(self.model_class, id=id)
        if gateway_mission.status != 1:  # Статус 1 = Черновик
            return Response(
                {"error": "Удаление разрешено только для черновиков"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Пометить миссию удалённой (установить дату удаления)
        gateway_mission.form_datetime = None
        gateway_mission.status = 5
        gateway_mission.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
class GatewayMissionCreators(APIView):
    model_class = Gateway_mission
    serializer_class = GatewayMissionSerializer
    def put(self, request, id, format=None):
        # Получаем заявку по id
        gateway_mission = get_object_or_404(self.model_class, id=id)

        # Проверяем обязательные поля
        status = request.data.get('status')
        if status not in [1, 2, 3, 4, 5]:
            return Response({"error": "Неверный статус заявки."}, status=status.HTTP_400_BAD_REQUEST)

        # Если меняем статус на завершен или отклонен, устанавливаем модератора и дату завершения
        if status in [3, 4]:  # Завершен или Отклонен
            moderator = request.data.get('moderator')
            if not moderator:
                return Response({"error": "Модератор не указан."}, status=status.HTTP_400_BAD_REQUEST)

            gateway_mission.moderator = moderator
            gateway_mission.complete_datetime = timezone.now()
            # Вычисляем стоимость и дату доставки при завершении заявки

        # Обновляем остальные поля
        serializer = self.serializer_class(gateway_mission, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class GatewayElementMissionDetail(APIView):
    model_class = gateway_element_and_mission
    serializer_class = GatewayElementMissionSerializer
    def delete(self, request, mission_id,element_id, format=None):
        mm_record = gateway_element_and_mission.objects.filter(
            mission_id=mission_id,
            element_id=element_id
        ).first()
        if not mm_record:
            return Response(
                {"error": "Элемент не найден в заявке"},
                status=status.HTTP_404_NOT_FOUND,
            )

            # Удалить запись
        mm_record.delete()

        return Response(
            {"message": "Элемент удалён из заявки", "mission_id": mission_id, "element_id": element_id},
            status=status.HTTP_200_OK,
        )

class UsersList(APIView):
    model_class = AuthUser
    serializer_class = UserSerializer

    def get(self, request, format=None):
        user = self.model_class.objects.all()
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data)
class RegisterView(APIView):
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

