from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
from django.shortcuts import render_to_response
from django.http import HttpResponse

from .models import DataFile, DataFrame
from .forms import DataFileForm

##  For importing a file
import os
from win import settings


## Pretty Print for debugging
from pprint import pprint
import json
from decimal import Decimal
import datetime

## For converting dates 
# from charts.views import CustomJSONEncoder

### Testing copying this function rather than including it for aws reasons

class CustomJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj, 'isoformat'): #handles both date and datetime objects
			return obj.isoformat()
 		elif isinstance(obj, datetime.timedelta):
 			return str(obj)
		elif isinstance(obj, Decimal):
			return float(obj)
		else:
			return json.JSONEncoder.default(self, obj)

# This should be changed later, defaults to string to avoid serialization isssues		
# class StringJSONEncoder(json.JSONEncoder):
# 	def default(self, obj):
# 		if hasattr(obj, 'isoformat'): #handles both date and datetime objects
# 			return obj.isoformat()
#  		elif hasattr(obj, 'total_seconds'):
# 		elif isinstance(obj, datetime.timedelta):
#  			return "string" #str(obj)
# 		elif isinstance(obj, Decimal):
# 			return float(obj)
# 		else:
# 			return str(obj)


################################## File Detail ##################################

class DataFileDetailView(TemplateView):
	model = DataFile
	template_name = "data/datafile_detail.html"
	
	def get(self, request, *args, **kwargs):
		context = super(DataFileDetailView, self).get_context_data(**kwargs)

		try:
			datafile = DataFile.objects.get(pk = self.kwargs['pk'])
		except Exception,e:
			context['debug'] = str(e)
		
		context['object'] = datafile
		
		return self.render_to_response(context)
	
	def post(self, request, *args, **kwargs):
		if(self.request.POST['id'] == 'name'):
			datafile = DataFile.objects.get(pk = self.kwargs['pk'])		
			datafile.name = self.request.POST['value']
			datafile.save()
			return HttpResponse(datafile.name)
		else:
			return HttpResponse('error')




################################## File Import ##################################

class DataFileImportView(TemplateView):
	template_name = "data/datafile_import.html"

	def get(self, request, *args, **kwargs):
		context = super(DataFileImportView, self).get_context_data(**kwargs)

		datafile = DataFile.objects.get(slug =  self.kwargs['slug'], pk = self.kwargs['pk'])
		new_dataframe = DataFrame(name = datafile.name)
		new_dataframe.save()
		import_status = new_dataframe.import_from_file(datafile)

		context['output'] = import_status['output']
		context['command'] = import_status['command']

		context['object'] = new_dataframe
		return self.render_to_response(context)

################################## Frame Detail ##################################

class DataFrameDetailView(TemplateView):
	model = DataFrame
	template_name = "data/dataframe_detail.html"
	
	def get(self, request, *args, **kwargs):
		context = super(DataFrameDetailView, self).get_context_data(**kwargs)

		try:
			dataframe = DataFrame.objects.get(pk = self.kwargs['pk'])
		except Exception,e:
			context['debug'] = str(e)
		
		context['object'] = dataframe
		
		(rows, column_names) = dataframe.get_data(nrows = 20)
		rows_as_list = list(rows)
		rows_as_list.insert(0, column_names)
		context['data_list'] = json.dumps(rows_as_list, cls=CustomJSONEncoder)
# 		context['data_list'] = json.dumps(rows_as_list, cls=StringJSONEncoder)

		return self.render_to_response(context)
	
	def post(self, request, *args, **kwargs):
		if(self.request.POST['id'] == 'name'):
			dataframe = DataFrame.objects.get(pk = self.kwargs['pk'])		
			dataframe.name = self.request.POST['value']
			dataframe.save()
			return HttpResponse(dataframe.name)
		else:
			return HttpResponse('error')


		
		
		
		
		
		