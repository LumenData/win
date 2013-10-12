from django.conf.urls import patterns, url
from . import views

# Importing for the list function-based views
from django.conf.urls.defaults import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
	url(r'^$', views.DataFrameListView.as_view(), name="list"),
	url(r'^import$', views.DataFrameCreateView.as_view(), name="import"),
	#url(r'^import$', "data.views.list", name="import"),
	#url(r'^import$', views.DataFrameCreate.as_view(), name="import"),
		
	url(r'^(?P<slug>[\w-]+)/$', views.DataFrameDetailView.as_view(), name="frame"),
	url(r'^(?P<slug>[\w-]+)/delete$', views.DataFrameDeleteView.as_view(), name="delete"),

	#Need to get this working for columns
	#url(r'^(?P<slug>[\w-]+)/$', views.DataFrameDetailView.as_view(), name="frame"),
)
