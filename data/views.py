from django.views.generic import TemplateView

class ImportView(TemplateView):
	template_name = "import_form.html"