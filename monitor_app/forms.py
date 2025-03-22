from django import forms
from .models import Collected

class CongestionForm(forms.ModelForm):
    class Meta:
        model = Collected
        fields = ["location", "congestion_level"]
        widgets = {
            "location" : forms.RadioSelect()
        }