from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^$', views.ImportView.as_view(), name="import"),
)
