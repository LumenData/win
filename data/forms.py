#from django import forms
from django.forms import ModelForm
from .models import DataFrame

class DataImportForm(ModelForm):
	class Meta:
		model = DataFrame