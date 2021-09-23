from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.air_quality_form, name='air_quality_insert'), # GET and POST for INSERT
    path('<int:id>/', views.air_quality_form, name='air_quality_update'), # GET and POST for UPDATE/EDIT
    path('list/', views.air_quality_list, name='air_quality_table'), #GET for RETREIVE and DISPLAY
    path('delete/<int:id>',views.air_quality_delete, name='air_quality_delete' )
]