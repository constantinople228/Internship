from django.urls import path
from . import views

app_name = 'pereval'

urlpatterns = [
    path('submitData/', views.submit_data, name='submit_data'),
    path('submitData/<int:id>/', views.get_pereval_by_id, name='get_pereval_by_id'),
    path('submitData/update/<int:id>/', views.update_pereval, name='update_pereval'),
    path('submitData/email/', views.get_perevals_by_user_email, name='get_perevals_by_user_email'),
]
