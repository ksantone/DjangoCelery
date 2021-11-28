from django.urls import path
from .views import pipeline_list_view, pipeline_detail_view, pipeline_execute_view

app_name = 'pipelines'
urlpatterns = [
    path('', pipeline_list_view, name='pipeline_list_view'),
    path('<int:id>/', pipeline_detail_view, name='pipeline_detail_view'),
    path('<int:id>/execute/', pipeline_execute_view, name='pipeline_execute_view'),
]