from django.conf.urls import patterns, url
# from django.views.generic import TemplateView
from views import AutoChartView;

urlpatterns = patterns('',
	url(r'^$', AutoChartView.as_view(), name="autochart"),
)
