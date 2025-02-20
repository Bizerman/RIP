import segno
import base64
from io import BytesIO
from datetime import datetime

def generate_mission_qr(mission, elements):
    """
    Генерирует QR-код для миссии.

    ВХ:
    mission: Gateway_mission - объект миссии
    elements: List[gateway_element_and_mission] - список элементов, связанных с миссией

    ВЫХ:
    str - QR-код в виде base64 строки
    """
    # Формируем информацию для QR-кода
    info = f"Миссия: {mission.id or ''}\n"
    info += f"Статус: {mission.get_status_display()}\n"
    info += f"Создатель: {mission.creator.username}\n"
    info += f"Создана: {mission.create_datetime.strftime('%d-%m-%Y %H:%M:%S')}\n"
    info += f"Плановая дата: {mission.plan_date.strftime('%d-%m-%Y %H:%M:%S') if mission.plan_date else 'Не указана'}\n\n"

    # Добавляем элементы миссии
    info += "Элементы:\n"
    for item in elements:
        element = item.element
        info += f"- {element.title}: {element.short_description}\n"
        if item.addition:
            info += f"  Комментарий: {item.addition}\n"

    # Генерация QR-кода
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    # Конвертация изображения в base64
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return qr_image_base64
