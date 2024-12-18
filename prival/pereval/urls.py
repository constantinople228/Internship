from django.urls import path
from . import views

app_name = 'pereval'

urlpatterns = [
    path('submitData/', views.submit_data, name='submit_data'),
]