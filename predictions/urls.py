from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from views import PredictionsView;

urlpatterns = patterns('',
	url(r'^$', PredictionsView.as_view(), name="home"),
)
