from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from views import ChartBuilderView, AutoChartView, AutoFilterView, PredictionPopoverView;

urlpatterns = patterns('',
	url(r'^$', ChartBuilderView.as_view(), name="home"),
	url(r'^autochart$', AutoChartView.as_view(), name="autochart"),
	url(r'^autofilter$', AutoFilterView.as_view(), name="autofilter"),
# 	url(r'^prediction_popover$', TemplateView.as_view(template_name="prediction_popover.html"), name="prediction_popover"),
	url(r'^prediction_popover$', PredictionPopoverView.as_view(), name="prediction_popover"),

)
