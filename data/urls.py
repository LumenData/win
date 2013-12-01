from django.conf.urls import patterns, url
from . import views
from .views import *
from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, DeleteView
from .models import DataFile, DataFrame
from .forms import DataFileForm
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
	url(r'^file$', ListView.as_view(model=DataFile), name="filelist"),
	url(r'^file/create$', CreateView.as_view(model=DataFile, form_class = DataFileForm), name="filecreate"),
# 	url(r'^file/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)$', DetailView.as_view(model=DataFile), name="filedetail"),
	url(r'^file/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)$', DataFileDetailView.as_view(model=DataFile), name="filedetail"),
	url(r'^file/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/delete$', DeleteView.as_view(model = DataFile, success_url = reverse_lazy('data:filelist')), name="filedelete"),
	url(r'^file/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/import$', views.DataFileImportView.as_view(), name="fileimport"),

	url(r'^frame$', ListView.as_view(model=DataFrame), name="framelist"),
 	url(r'^frame/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)$', DataFrameDetailView.as_view(), name="framedetail"),
	url(r'^frame/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/delete$', DeleteView.as_view(model = DataFrame, success_url = reverse_lazy('data:framelist')), name="framedelete"),
 	url(r'^frame/(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/(?P<column_name>.+)/unique_values.json$', DataColumnUniqueListView.as_view(), name="column-unique-list"),


# 	url(r'^pie$', 'data.views.pie', name="pie"),
)
