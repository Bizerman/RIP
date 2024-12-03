from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        bucket_name = "img-for-rip"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        object_path = f"images/{image_name}"
        client.put_object(bucket_name, object_path, file_object, file_object.size)
        return f"http://localhost:9000/{bucket_name}/{object_path}"
    except Exception as e:
        return {"error": str(e)}


def add_img(new_gateway_el, img):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    img_obj_name = f"{new_gateway_el.title}.png"

    if not img:
        return {"error": "Нет файла для изображения логотипа."}

    # Загрузка файла
    result = process_file_upload(img, client, img_obj_name)

    if isinstance(result, dict) and 'error' in result:
        # Возвращаем ошибку, если она произошла
        return result

    # Сохранение URL в модели
    new_gateway_el.img_url = result
    new_gateway_el.save()

    return {"message": "success", "img_url": result}
def del_img(gateway_el):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    img_url = gateway_el.img_url
    if not img_url:
        return
    try:
        bucket_name = "img-for-rip"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        object_path = f"images/{gateway_el.title}.png"
        client.remove_object(bucket_name, object_path)
    except Exception as e:
        return {"Ошибка при удалении файла из MinIO:": str(e)}

