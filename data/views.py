from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
#All these imports for function based list view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from .models import DataFile
from .forms import DataFileForm

class DataFileListView(ListView):
	model = DataFile
	def get_context_data(self, **kwargs):
		context = super(DataFileListView, self).get_context_data(**kwargs)
		return context

class DataFileDetailView(DetailView):
	model = DataFile
	

class DataFileCreateView(CreateView):
    model = DataFile
    form_class = DataFileForm

    def get(self, request, *args, **kwargs):
        return super(DataFileCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DataFileCreateView, self).post(request, *args, **kwargs)

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
	
	
# def list(request):
# 	# Handle file upload
# 	if request.method == 'POST':
# 		form = DataFileForm(request.POST, request.FILES)
# 		if form.is_valid():
# 			newdoc = DataFile(
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
# 		form = DataFileForm() # A empty, unbound form
# 
# 	# Load documents for the list page
# 	documents = DataFile.objects.all()
# 
# 	# Render list page with the documents and the form
# 	return render_to_response(
# 		'data/import.html',
# 		{'documents': documents, 'form': form},
# 		context_instance=RequestContext(request)
# 	)




	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	