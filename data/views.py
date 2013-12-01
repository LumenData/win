from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
from django.shortcuts import render_to_response
from django.http import HttpResponse

from .models import DataFile, DataFrame
from .forms import DataFileForm

##  For importing a file
import os
from win import settings

## For serializing to JSON 
import json
from decimal import Decimal
import datetime


class CustomJSONEncoder(json.JSONEncoder):
	## Testing copying this function rather than including it for aws reasons
	# from charts.views import CustomJSONEncoder (not used)
	
	def default(self, obj):
		if hasattr(obj, 'isoformat'): #handles both date and datetime objects
			return obj.isoformat()
		elif isinstance(obj, datetime.timedelta):
			return str(obj)
		elif isinstance(obj, Decimal):
			return float(obj)
		else:
			return json.JSONEncoder.default(self, obj)

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

		return self.render_to_response(context)
	
	def post(self, request, *args, **kwargs):
		if(self.request.POST['id'] == 'name'):
			dataframe = DataFrame.objects.get(pk = self.kwargs['pk'])		
			dataframe.name = self.request.POST['value']
			dataframe.save()
			return HttpResponse(dataframe.name)
		else:
			return HttpResponse('error')

################################## Column - Unique Values ##################################
		
class DataColumnUniqueListView(TemplateView):
	def get(self, request, *args, **kwargs):
		column_name = kwargs['column_name']
		search_term = request.GET.get('q')

		try:
			dataframe = DataFrame.objects.get(pk = self.kwargs['pk'])
		except Exception,e:
			context['debug'] = str(e)
			
		if search_term == "*":
			query = "SELECT distinct(%s) FROM %s LIMIT 20" % (column_name, dataframe.db_table_name);
		else:
			query = "SELECT distinct(%s) FROM %s WHERE %s LIKE '%%%s%%' LIMIT 20" % (column_name, dataframe.db_table_name, column_name, search_term);
		
		uniques_as_list_of_dicts = dataframe.query_results(query)[0]
		
 		## uniques_as_list_of_dicts lookst like [{'my_col': value1}, {'my_col': value2}, ...]
		## but we need [value1, value2, ...]
		uniques_as_list = [item[column_name] for item in uniques_as_list_of_dicts]

		return HttpResponse(json.dumps(uniques_as_list))
		