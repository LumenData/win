from django.conf.urls import patterns, url
from . import views

# Importing for the list function-based views
from django.conf.urls.defaults import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
	url(r'^$', views.DataFrameListView.as_view(), name="list"),
	url(r'^create$', views.DataFrameCreateView.as_view(), name="create"),
	
	url(r'^(?P<slug>[\w-]+)/$', views.DataFrameDetailView.as_view(), name="frame"),
	url(r'^(?P<slug>[\w-]+)/importdata$', views.DataFrameDeleteView.as_view(), name="importdata"),
	url(r'^(?P<slug>[\w-]+)/delete$', views.DataFrameDeleteView.as_view(), name="delete"),
	#url(r'^(?P<slug>[\w-]+)/delete$', views.DataFrameDeleteView.as_view(), name="delete"),

	#Need to get this working for columns
	#url(r'^(?P<slug>[\w-]+)/$', views.DataFrameDetailView.as_view(), name="frame"),
)
