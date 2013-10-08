from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from .models import DataFrame
#from .forms import DataImportForm

class DataFrameListView(ListView):
	model = DataFrame
	def get_context_data(self, **kwargs):
		context = super(DataFrameListView, self).get_context_data(**kwargs)
		return context

class DataFrameDetailView(DetailView):
	model = DataFrame

#def create(request):
#	if request.POST:
#		form = DataImportForm(request.POST)
#		if form.is_valid():
#			form.save()
#			return HttpResponseRedirect('/data')
#	else:
#		form = DataImportForm()
#	args = {}
#	args.update(csrf(request))
#	args['form'] = form	
#	return render_to_response('data_import.html',args)
	
# Not yet finished, still using the above function based view
class DataFrameCreate(CreateView):
	model = DataFrame