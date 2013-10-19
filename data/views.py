from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
#All these imports for function based list view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from .models import DataFile
from .forms import DataFileForm


def pie(request):
	context = {'values': [['foo', 32], ['bar', 64], ['baz', 96]]}
	return render_to_response('data/piechart.html', context)

## File List
class DataFileListView(ListView):
	model = DataFile
	def get_context_data(self, **kwargs):
		context = super(DataFileListView, self).get_context_data(**kwargs)
		return context


## File Detail
class DataFileDetailView(DetailView):
	model = DataFile


## File Create
class DataFileCreateView(CreateView):
    model = DataFile
    form_class = DataFileForm

    def get(self, request, *args, **kwargs):
        return super(DataFileCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DataFileCreateView, self).post(request, *args, **kwargs)


## File Delete
class DataFileDeleteView(DeleteView):
	model = DataFile	
	def get_object(self, queryset=None):
		obj = super(DataFileDeleteView, self).get_object()
		if not obj.owner == self.request.user:
			raise Http404
		else:
			obj.file.delete()
		return obj	
	success_url = '/data/'


##  Import a file
import csv
import MySQLdb

class DataFileImportView(TemplateView):
	template_name = "data/datafile_detail_import.html"
	
	def get(self, request, *args, **kwargs):
		context = super(DataFileImportView, self).get_context_data(**kwargs)
		slug = self.kwargs['slug']

		datafile = DataFile.objects.get(slug = slug)
		dataiter = datafile.file.__iter__()
		
		header_row = dataiter.next();
		
		
		context['testvar'] = header_row
		return self.render_to_response(context)


	
	
	
	
	
	
	