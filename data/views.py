from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
#All these imports for function based list view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from .models import DataFile, DataFrame
from .forms import DataFileForm

##  Import a file
# import csv
import os
from win import settings

class DataFileImportView(TemplateView):
	template_name = "data/datafile_detail_import.html"

	def get(self, request, *args, **kwargs):
		context = super(DataFileImportView, self).get_context_data(**kwargs)
		slug = self.kwargs['slug']

		datafile = DataFile.objects.get(slug = slug)

		db_name = settings.DATABASES['default']['NAME']		
		db_user = settings.DATABASES['default']['USER']	
		db_password = settings.DATABASES['default']['PASSWORD']	
		db_table = '_userdata' + '_U' + str(datafile.owner) + '_DF' + str(datafile.pk)

		new_dataframe_name = datafile.name
		new_dataframe = DataFrame(name=new_dataframe_name, db_table_name = db_table)
		new_dataframe.save()
	
		import_string = "python data/csv2mysql.py --table=%s --database=%s --user=%s --password=%s %s" % (db_table, db_name, db_user, db_password, datafile.file.path)
		import_status = os.popen(import_string).read()
		
		context['testvar'] = import_status
		
		return self.render_to_response(context)

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



	
	
	
	
	
	