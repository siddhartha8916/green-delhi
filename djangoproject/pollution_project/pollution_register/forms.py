from django import forms
from .models import air_quality

class AQI_form(forms.ModelForm):
    class Meta:
        model = air_quality
        fields = '__all__'
        labels = {'aqi' : 'AQI',
                  'pm25': 'PM 2.5',
                  'pm10' : 'PM 10'}
        widgets = {
            'date' : forms.DateInput(attrs={'type':'date'})
            }


