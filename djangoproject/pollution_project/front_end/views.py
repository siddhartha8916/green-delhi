from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'front_end/index.html')

def vehicle(request):
    return render(request,'front_end/vehicle.html')

def stories(request):
    return render(request,'front_end/stories.html')