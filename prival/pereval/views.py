from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .core.database import FSTRDatabase
import base64
import logging

logging.basicConfig(level=logging.INFO)
db = FSTRDatabase()


@api_view(['POST'])
def submit_data(request):
    try:
        data = request.data
        if not all(key in data for key in ['user', 'coords', 'levels', 'prival', 'images']):
            return Response({"status": "error", "message": "Недостающие поля в запросе"}, status=status.HTTP_400_BAD_REQUEST)
        user_data = data.get('user', {})
        coords_data = data.get('coords', {})
        levels_data = data.get('levels', {})
        pereval_data = data.get('prival', {})
        images_data = data.get('images', [])

        if not all(key in user_data for key in ['email', 'fam', 'name', 'otc', 'phone']):
            return Response({"status": "error", "message": "Недостающие поля в user"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(key in coords_data for key in ['latitude', 'longitude', 'height']):
            return Response({"status": "error", "message": "Недостающие поля в coords"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(key in pereval_data for key in ['date_added', 'beauty_title', 'title']):
             return Response({"status": "error", "message": "Недостающие поля в prival"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(images_data, list):
             return Response({"status": "error", "message": "images должно быть списком"}, status=status.HTTP_400_BAD_REQUEST)
        try:
             float(coords_data.get('latitude'))
             float(coords_data.get('longitude'))
             int(coords_data.get('height'))
        except ValueError:
             return Response({"status":"error", "message":"Неправильный формат чисел в coords"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = db.add_user(
                user_data.get('email', ''),
                user_data.get('fam', ''),
                user_data.get('name', ''),
                user_data.get('otc', ''),
                user_data.get('phone', ''))
        except Exception as e:
            logging.error(f"Ошибка при добавлении пользователя: {str(e)}")
            return Response({"status": "error", "message": f"Ошибка при добавлении пользователя"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            coord_id = db.add_coord(
                coords_data.get('latitude'),
                coords_data.get('longitude'),
                coords_data.get('height'))
        except Exception as e:
            logging.error(f"Ошибка при добавлении координат: {str(e)}")
            return Response({"status": "error", "message": f"Ошибка при добавлении координат"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            level_id = db.add_levels(
                levels_data.get('winter'),
                levels_data.get('summer'),
                levels_data.get('autumn'),
                levels_data.get('spring'))
        except Exception as e:
            logging.error(f"Ошибка при добавлении уровней: {str(e)}")
            return Response({"status": "error", "message": f"Ошибка при добавлении уровней"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            pereval_id = db.add_pereval(
                user_id,
                coord_id,
                level_id,
                pereval_data.get('date_added'),
                pereval_data.get('beauty_title'),
                pereval_data.get('title'),
                pereval_data.get('other_titles'),
                pereval_data.get('connect')
            )
        except Exception as e:
            logging.error(f"Ошибка при добавлении перевала: {str(e)}")
            return Response({"status": "error", "message": f"Ошибка при добавлении перевала"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        for image_data in images_data:
            try:
               if not isinstance(image_data.get('img', ''), str):
                 return Response({"status":"error", "message":"img должен быть строкой"}, status=status.HTTP_400_BAD_REQUEST)
               if not image_data.get('img', ''):
                    return Response({"status":"error", "message": "В images отсутствует поле img"}, status=status.HTTP_400_BAD_REQUEST)
               img_id = db.add_image(base64.b64decode(image_data.get('img')))
               if img_id and pereval_id:
                    db.add_pereval_image(pereval_id, img_id)
            except Exception as e:
                  logging.error(f"Ошибка при добавлении изображения: {str(e)}")
                  return Response({"status":"error", "message":"Ошибка при добавлении изображения"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if user_id and coord_id and level_id and pereval_id:
             return Response({"status": "success", "message": "Data added successfully", "pereval_id":pereval_id}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "message": "Error adding data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logging.error(f"Внутренняя ошибка сервера: {str(e)}")
        return Response({"status": "error", "message": f"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_pereval_by_id(request, id):
    try:
        pereval = db.get_pereval_by_id(id)
        if pereval:
            return Response(pereval, status=status.HTTP_200_OK)
        else:
            return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Ошибка при получении перевала по id: {str(e)}")
        return Response({"state": 0, "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def update_pereval(request, id):
    try:
        data = request.data
        pereval = db.get_pereval_by_id(id)
        if not pereval:
             return Response({"state": 0, "message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)
        if pereval['prival'][9] != 'new': # Поле status имеет индекс 9
            return Response({"state": 0, "message": "Перевал не в статусе new"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(key in data for key in ['coords', 'levels', 'prival', 'images']):
           return Response({"status": "error", "message": "Недостающие поля в запросе"}, status=status.HTTP_400_BAD_REQUEST)
        coords_data = data.get('coords', {})
        levels_data = data.get('levels', {})
        pereval_data = data.get('prival', {})
        images_data = data.get('images', [])
        if not all(key in coords_data for key in ['latitude', 'longitude', 'height']):
             return Response({"status": "error", "message": "Недостающие поля в coords"}, status=status.HTTP_400_BAD_REQUEST)
        if not all(key in pereval_data for key in ['date_added', 'beauty_title', 'title']):
             return Response({"status": "error", "message": "Недостающие поля в prival"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(images_data, list):
            return Response({"status": "error", "message": "images должно быть списком"}, status=status.HTTP_400_BAD_REQUEST)
        try:
             float(coords_data.get('latitude'))
             float(coords_data.get('longitude'))
             int(coords_data.get('height'))
        except ValueError:
             return Response({"status":"error", "message":"Неправильный формат чисел в coords"}, status=status.HTTP_400_BAD_REQUEST)
        coord_id = db.update_coord(
                id,
                coords_data.get('latitude'),
                coords_data.get('longitude'),
                coords_data.get('height'))

        level_id = db.update_levels(
            id,
            levels_data.get('winter'),
            levels_data.get('summer'),
            levels_data.get('autumn'),
            levels_data.get('spring'))

        pereval_id = db.update_pereval(
            id,
            pereval_data.get('date_added'),
            pereval_data.get('beauty_title'),
            pereval_data.get('title'),
            pereval_data.get('other_titles'),
            pereval_data.get('connect')
        )
        db.delete_pereval_images(id)
        for image_data in images_data:
            try:
               if not isinstance(image_data.get('img', ''), str):
                 return Response({"status":"error", "message":"img должен быть строкой"}, status=status.HTTP_400_BAD_REQUEST)
               if not image_data.get('img', ''):
                  return Response({"status":"error", "message": "В images отсутствует поле img"}, status=status.HTTP_400_BAD_REQUEST)
               img_id = db.add_image(base64.b64decode(image_data.get('img')))
               if img_id and pereval_id:
                    db.add_pereval_image(pereval_id, img_id)
            except Exception as e:
                 logging.error(f"Ошибка при добавлении изображения: {str(e)}")
                 return Response({"status":"error", "message":"Ошибка при добавлении изображения"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if  coord_id and level_id and pereval_id:
            return Response({"state": 1, "message": "Data updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"state": 0, "message": "Error updating data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logging.error(f"Ошибка при обновлении перевала: {str(e)}")
        return Response({"state": 0, "message": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_perevals_by_user_email(request):
    email = request.query_params.get('user__email')
    if not email:
        return Response({"state":0, "message": "Не указан email"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        perevals = db.get_perevals_by_user_email(email)
        return Response(perevals, status=status.HTTP_200_OK)
    except Exception as e:
       logging.error(f"Ошибка при получении перевалов по email {email}: {str(e)}")
       return Response({"state": 0, "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
