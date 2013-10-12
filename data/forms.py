from django import forms
from django.forms import ModelForm

#class DocumentForm(forms.Form):
#    docfile = forms.FileField(
#        label='Select a file',
#        help_text='max. 42 megabytes'
#    )

from .models import DataFrame

class DataFrameForm(ModelForm):
	class Meta:
		model = DataFrame