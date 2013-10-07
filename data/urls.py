from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^$', views.DataFrameListView.as_view(), name="list"),
	#url(r'^import$', views.DataImportView.as_view(), name="import"),
	#url(r'^import$', views.create, name="import"),
	url(r'^import$', views.DataFrameCreate.as_view(), name="import"),	
)
