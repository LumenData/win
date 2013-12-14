from django.views.generic import TemplateView
from data.models import DataFrame

import numpy
import scipy
import sklearn

####################### View - Chart Builder #######################

class PredictionsView(TemplateView):
	template_name = "predictions.html"

	def get(self, request, *args, **kwargs):
		context = super(PredictionsView, self).get_context_data(**kwargs)
		
		dataframe_id = request.GET.get('dataframe_id')
		target_name = request.GET.get('target_name')
		training_nrow = request.GET.get('training_nrow')
		
		try:
			dataframe = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = "No DataFrame Found"
			return self.render_to_response(context)

		from sklearn import datasets
		iris = datasets.load_iris()

		context['debug'] = iris


		return self.render_to_response(context)
