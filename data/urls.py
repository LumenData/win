from django.conf.urls import patterns, url
from . import views

# Importing for the list function-based views
from django.conf.urls.defaults import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
	url(r'^$', views.DataFileListView.as_view(), name="filelist"),
	url(r'^create$', views.DataFileCreateView.as_view(), name="filecreate"),
	url(r'^pie$', 'data.views.pie', name="pie"),

 	url(r'^(?P<slug>[\w-]+)$', views.DataFileDetailView.as_view(), name="filedetail"),
	url(r'^(?P<slug>[\w-]+)/delete$', views.DataFileDeleteView.as_view(), name="filedelete"),

	url(r'^(?P<slug>[\w-]+)/import$', views.DataFileImportView.as_view(), name="fileimport"),

)
