from django.shortcuts import render, redirect
from .forms import AQI_form
from .models import air_quality

# Create your views here.

def air_quality_list(request):
    context = {'air_quality_list': air_quality.objects.all().order_by('-id')[:10]}
    return render(request, "pollution_register/AQI_list.html", context)


def air_quality_delete(request,id):
    aqi_element = air_quality.objects.get(pk=id)
    aqi_element.delete()
    return redirect('/air_quality/list')