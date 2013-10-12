from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
#All these imports for function based list view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from .models import DataFrame
from .forms import DataFrameForm

class DataFrameListView(ListView):
	model = DataFrame
	def get_context_data(self, **kwargs):
		context = super(DataFrameListView, self).get_context_data(**kwargs)
		return context

class DataFrameDetailView(DetailView):
	model = DataFrame
	

class DataFrameCreateView(CreateView):
    model = DataFrame
    form_class = DataFrameForm

    def get(self, request, *args, **kwargs):
        return super(DataFrameCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DataFrameCreateView, self).post(request, *args, **kwargs)

class DataFrameDeleteView(DeleteView):
	model = DataFrame
	success_url = '/data/'
	
	
# 	def get_object(self, queryset=None):
# 		obj = super(DataFrameDeleteView, self).get_object()
# 		if not obj.owner == self.request.user:
# 			raise Http404
# 		return obj

	
# def list(request):
# 	# Handle file upload
# 	if request.method == 'POST':
# 		form = DataFrameForm(request.POST, request.FILES)
# 		if form.is_valid():
# 			newdoc = DataFrame(
# 				name = request.POST['name'],
# 				description = request.POST['description'],
# # 				owner = self.request.user,
# 				slug = request.POST['slug'],
# 				db_table_name = request.POST['db_table_name'],
# 				docfile = request.FILES['docfile']
# 			)
# 			newdoc.save()
# 
# 			# Redirect to the document list after POST
# # 			return HttpResponseRedirect(reverse('data:import'))
# 			return HttpResponseRedirect(newdoc.get_absolute_url())
# 	else:
# 		form = DataFrameForm() # A empty, unbound form
# 
# 	# Load documents for the list page
# 	documents = DataFrame.objects.all()
# 
# 	# Render list page with the documents and the form
# 	return render_to_response(
# 		'data/import.html',
# 		{'documents': documents, 'form': form},
# 		context_instance=RequestContext(request)
# 	)




	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	