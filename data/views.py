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

class DataFileImportView(TemplateView):
	template_name = "data/datafile_import.html"

	def get(self, request, *args, **kwargs):
		context = super(DataFileImportView, self).get_context_data(**kwargs)
		slug = self.kwargs['slug']

		datafile = DataFile.objects.get(slug = slug)

 		new_dataframe = DataFrame(name = datafile.name)
 		new_dataframe.save()
 		import_status = new_dataframe.import_from_file(datafile)

		context['testvar'] = import_status
		context['object'] = new_dataframe
		return self.render_to_response(context)

def pie(request):
	context = {'values': [['foo', 32], ['bar', 64], ['baz', 96]]}
	return render_to_response('data/piechart.html', context)
	
class DataFrameDetailView(DetailView):
	model = DataFrame
	
	def post(self, request, *args, **kwargs):
		if(self.request.POST['id'] == 'name'):
			dataframe = DataFrame.objects.get(pk = self.kwargs['pk'])		
			dataframe.name = self.request.POST['value']
			dataframe.save()
 			return HttpResponse(dataframe.name)
 		else:
 			return HttpResponse('error')

		
		
		
		
		
		
		
		
		
		