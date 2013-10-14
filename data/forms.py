from django import forms
from django.forms import ModelForm

from .models import DataFile

class DataFileForm(ModelForm):
	class Meta:
		model = DataFile