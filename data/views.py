from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
#All these imports for function based list view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, reverse_lazy

from .models import DataFile, DataFrame
from .forms import DataFileForm

##  Import a file
import os
from win import settings

## Get Pretty Print for debugging
from pprint import pprint

class DataFileImportView(TemplateView):
	template_name = "data/datafile_import.html"

	def get(self, request, *args, **kwargs):
		context = super(DataFileImportView, self).get_context_data(**kwargs)
		slug = self.kwargs['slug']

		datafile = DataFile.objects.get(slug = slug)

		new_dataframe = DataFrame(name = datafile.name)
		new_dataframe.save()
		import_status = new_dataframe.import_from_file(datafile)

		context['output'] = import_status['output']
		context['command'] = import_status['command']
		
		context['object'] = new_dataframe
		return self.render_to_response(context)


def pie(request):
	context = {'values': [['foo', 32], ['bar', 64], ['baz', 96]]}
	return render_to_response('data/piechart.html', context)

	
class DataFrameDetailView(TemplateView):
	model = DataFrame
	template_name = "data/dataframe_detail.html"
	
	def get(self, request, *args, **kwargs):
		context = super(DataFrameDetailView, self).get_context_data(**kwargs)
		thisslug = self.kwargs['slug']
		thispk = self.kwargs['pk']
		
		dataframe = DataFrame.objects.get(slug = thisslug, pk = thispk)
		context['object'] = dataframe
		context['thedata'] = dataframe.get_data()[0]
		
		return self.render_to_response(context)
	
	def post(self, request, *args, **kwargs):
		if(self.request.POST['id'] == 'name'):
			dataframe = DataFrame.objects.get(pk = self.kwargs['pk'])		
			dataframe.name = self.request.POST['value']
			dataframe.save()
			return HttpResponse(dataframe.name)
		else:
			return HttpResponse('error')

		
		
		
		
		
		
		
		
		
		