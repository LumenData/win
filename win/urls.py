from django.conf.urls import patterns, include, url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
	url(r'^$', TemplateView.as_view(template_name = "index.html"), name="home"),
	url(r'^data/', include("data.urls",namespace="data")),
	url(r'^charts/', include("charts.urls",namespace="charts")),	
	url(r'^predictions/', include("predictions.urls",namespace="predictions")),	
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)