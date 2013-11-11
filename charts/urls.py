from django.conf.urls import patterns, url
# from django.views.generic import TemplateView
from views import PieChartView;

urlpatterns = patterns('',
	url(r'^$', PieChartView.as_view(), name="pie"),
)
