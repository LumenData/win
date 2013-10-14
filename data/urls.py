from django.conf.urls import patterns, url
from . import views

# Importing for the list function-based views
from django.conf.urls.defaults import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
	url(r'^$', views.DataFileListView.as_view(), name="list"),
	url(r'^create$', views.DataFileCreateView.as_view(), name="create"),
	
	url(r'^(?P<slug>[\w-]+)/$', views.DataFileDetailView.as_view(), name="file"),
	url(r'^(?P<slug>[\w-]+)/importdata$', views.DataFileDeleteView.as_view(), name="importdata"),
	url(r'^(?P<slug>[\w-]+)/delete$', views.DataFileDeleteView.as_view(), name="delete"),
)
