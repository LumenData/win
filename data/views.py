from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
#All these imports for function based list view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
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

		new_dataframe_name = datafile.name
		new_dataframe = DataFrame(name=new_dataframe_name)
		import_status = new_dataframe.import_from_file(datafile)
		new_dataframe.save()

		context['testvar'] = import_status
		context['object'] = new_dataframe
		return self.render_to_response(context)

def pie(request):
	context = {'values': [['foo', 32], ['bar', 64], ['baz', 96]]}
	return render_to_response('data/piechart.html', context)


# ## File Delete
# class DataFileDeleteView(DeleteView):
# 	model = DataFile	
# 	success_url = reverse_lazy('data:filelist')
# 


## Frame Delete

# class DataFrameDeleteView(DeleteView):
# 	model = DataFrame
# 	success_url = reverse_lazy('data:framelist')




	
	
