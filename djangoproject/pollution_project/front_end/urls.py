from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('vehicle_pollution',views.vehicle,name='vehicle'),
    path('stories',views.vehicle,name='stories')

]


