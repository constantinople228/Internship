from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .core.database import FSTRDatabase
import base64


db = FSTRDatabase()


@api_view(['POST'])
def submit_data(request):
    try:
        data = request.data
        user_data = data.get('user', {})
        coords_data = data.get('coords', {})
        levels_data = data.get('levels', {})
        pereval_data = data.get('prival', {})
        images_data = data.get('images', [])
        user_id = db.add_user(
            user_data.get('email'),
            user_data.get('fam'),
            user_data.get('name'),
            user_data.get('otc'),
            user_data.get('phone'))

        coord_id = db.add_coord(
            coords_data.get('latitude'),
            coords_data.get('longitude'),
            coords_data.get('height'))

        level_id = db.add_levels(
            levels_data.get('winter'),
            levels_data.get('summer'),
            levels_data.get('autumn'),
            levels_data.get('spring'))

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
        for image_data in images_data:
              img_id = db.add_image(base64.b64decode(image_data.get('img')))
              if img_id and pereval_id:
                    db.add_pereval_image(pereval_id, img_id)

        if user_id and coord_id and level_id and pereval_id:
            return Response({"status": "success", "message": "Data added successfully", "pereval_id":pereval_id}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "message": "Error adding data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
         print(e)
         return Response({"status": "error", "message": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
