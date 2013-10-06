from django.http import HttpResponse

#def home(request):
#    return HttpResponse("Hello from django, try out <a href='/admin/'>/admin/</a>\n")
    
from django.views.generic import TemplateView

class HomepageView(TemplateView):
	template_name = "index.html"