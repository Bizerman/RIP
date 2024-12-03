from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from gateway.minio import add_img, del_img
from gateway.models import Gateway_el, AuthUser, Gateway_mission, gateway_element_and_mission
from gateway.serializers import GatewayElementSerializer, GatewayMissionSerializer, \
    GatewayElementMissionSerializer, GatewayMissionAdditionSerializer, GatewayElementTypeSerializer, \
    UserRegistrationSerializer, UserLoginSerializer, GatewayElementWithoutImg


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
        gateway_elements = self.model_class.objects.all().order_by('id')
        draft_mission = Gateway_mission.objects.filter(status=1).first()
        if draft_mission is None:
            draft_mission = Gateway_mission.objects.create()
            draft_mission.creator = user1
            draft_mission.create_datetime = timezone.now()
            draft_mission.save()

        element_count = gateway_element_and_mission.objects.filter(mission=draft_mission).count()
        response_data = {
            "elements": self.serializer_class(gateway_elements, many=True).data,
            "draft_mission_id": draft_mission.id,
            "draft_element_count": element_count,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        serializer = GatewayElementWithoutImg(data=request.data)
        if serializer.is_valid():
            gateway_element = serializer.save()
            return Response(GatewayElementWithoutImg(gateway_element).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Post'])
def add_element_to_draft(request, id, format=None):
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

    return Response({"mission_id": draft_mission.id}, status=status.HTTP_201_CREATED)


@api_view(['Post'])
def gateway_element_img_update(request, id, format=None):

    gateway_element = get_object_or_404(Gateway_el, id=id)
    new_image = request.FILES.get("img")

    if not new_image:
        return Response({"error": "Изображение не предоставлено"}, status=status.HTTP_400_BAD_REQUEST)

    # Обработка изображения
    img_result = add_img(gateway_element, new_image)

    if isinstance(img_result, dict) and 'error' in img_result:
        return Response(img_result, status=status.HTTP_400_BAD_REQUEST)

    # Сериализация данных для ответа
    serialized_data = GatewayElementSerializer(gateway_element).data
    return Response({"img_url": serialized_data.get('img_url')}, status=status.HTTP_200_OK)


class GatewayElementsDetail(APIView):
    model_class = Gateway_el
    serializer_class = GatewayElementSerializer

    def get(self, request, id, format=None):
        gateway_element = get_object_or_404(self.model_class, id=id)
        serializer = self.serializer_class(gateway_element)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        gateway_element = get_object_or_404(self.model_class, id=id)
        serializer = GatewayElementWithoutImg(gateway_element, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        gateway_element = get_object_or_404(self.model_class, id=id)
        del_img(gateway_element)
        gateway_element_and_mission.objects.filter(element=gateway_element).delete()
        gateway_element.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Put'])
def gateway_element_update(request, id, format=None):
    gateway_element = get_object_or_404(Gateway_el, id=id)
    serializer = GatewayElementSerializer(gateway_element, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get'])
def gateway_missions_list(request, format=None):
    gateway_els = Gateway_mission.objects.exclude(status='5').exclude(status='1')

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
    serializer = GatewayMissionSerializer(gateway_els, many=True)
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
        gateway_mission = get_object_or_404(self.model_class, id=id)
        gateway_elements = gateway_element_and_mission.objects.filter(mission=gateway_mission)
        # Сериализуем элементы
        elements = [GatewayElementSerializer(el.element).data for el in gateway_elements]
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
        if gateway_mission.status not in [1,2]:
            return Response({'error': 'Миссию уже нельзя изменить!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = GatewayMissionAdditionSerializer(gateway_mission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        gateway_mission = get_object_or_404(self.model_class, id=id)
        if gateway_mission.status == 1:  # Статус 1 = Черновик
            return Response(
                {"error": "Удаление запрещено для черновиков"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Пометить миссию удалённой (установить дату удаления)
        gateway_mission.form_datetime = None
        gateway_mission.status = 5
        gateway_mission.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Put'])
def gateway_mission_form(request, format=None):
    # Получаем заявку по id
    gateway_mission = Gateway_mission.objects.filter(status=1).first()
    if not gateway_mission:
        return Response({'error':'Элементы в миссии отсутствуют'},status=status.HTTP_404_NOT_FOUND)
    serializer = GatewayMissionSerializer(gateway_mission, data=request.data, partial=True)
    # Проверяем обязательные поля
    if gateway_mission.create_datetime > timezone.now():
        return Response({"error": "Неверное время создания миссии."}, status=status.HTTP_400_BAD_REQUEST)
    creator = get_object_or_404(AuthUser, username=gateway_mission.creator.username)
    if not creator:
        return Response({"error": "Неверный создатель миссии."}, status=status.HTTP_400_BAD_REQUEST)
    gateway_mission.status = 2
    gateway_mission.form_datetime = timezone.now()
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['put'])
def gateway_mission_complete(request, id, format=None):
    model_class = Gateway_mission
    serializer_class = GatewayMissionSerializer

    # Получаем заявку по id
    gateway_mission = get_object_or_404(model_class, id=id)
    serializer = serializer_class(gateway_mission, data=request.data, partial=True)
    if gateway_mission.status != 2:
        return Response({"error": "Миссия не сформированна, либо уже одобрена"}, status=status.HTTP_400_BAD_REQUEST)
    # Если меняем статус на завершен или отклонен, устанавливаем модератора и дату завершения
    mission_status = int(serializer.initial_data['status'])
    if mission_status in [3, 4]:  # Завершен или Отклонен
        gateway_mission.status = mission_status
        gateway_mission.moderator = user()
        gateway_mission.complete_datetime = timezone.now()
        gateway_mission.plan_date = timezone.now() + timezone.timedelta(days=10000)
    #     # Вычисляем стоимость и дату доставки при завершении заявки
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GatewayElementMissionDetail(APIView):
    model_class = gateway_element_and_mission
    serializer_class = GatewayElementMissionSerializer

    def put(self, request, mission_id, element_id, format=None):
        model_class = gateway_element_and_mission
        serializer_class = GatewayElementTypeSerializer

        mm_record = get_object_or_404(model_class, mission_id=mission_id, element_id=element_id)
        mm_record.element_type = request.data['element_type']
        serializer = serializer_class(mm_record, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)  # Возвращает данные с текстовым значением `element_type`
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


@api_view(['POST'])
def Registration(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Сохраняем пользователя
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Put'])
def ChangeProfile(request, id):
    user = get_object_or_404(AuthUser, id=id)
    serializer = UserRegistrationSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Профиль успешно изменен"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['Post'])
def Authentication(request):
    serializer = UserLoginSerializer(AuthUser, data=request.data, partial=True)
    if serializer.is_valid():
        user = get_object_or_404(AuthUser, username=request.username)
        user.last_login = timezone.now()
        user.is_active = True
        serializer.save()
        return Response({"message": "Профиль авторизован"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['Post'])
def Deathtorization(request, id):
    serializer = UserLoginSerializer(AuthUser, data=request.data, partial=True)
    if serializer.is_valid():
        user = get_object_or_404(AuthUser, id=id)
        user.is_active = False
        serializer.save()
        return Response({"message": "Вы вышли из профиля."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
