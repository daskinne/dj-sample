from django import forms
from roshee.models import Deal
from django.forms import ModelForm

class DealForm(ModelForm):
    class Meta:
        model = Deal
        fields=['name','description']

class MessageForm(forms.Form):
    message = forms.CharField(max_length=200)