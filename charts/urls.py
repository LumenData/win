from django.conf.urls import patterns, url
# from django.views.generic import TemplateView
from views import ChartBuilderView, AutoChartView, AutoFilterView;

urlpatterns = patterns('',
	url(r'^$', ChartBuilderView.as_view(), name="home"),
	url(r'^autochart$', AutoChartView.as_view(), name="autochart"),
	url(r'^autofilter$', AutoFilterView.as_view(), name="autofilter"),
)
