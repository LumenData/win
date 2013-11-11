from django.views.generic import TemplateView
from data.models import DataFrame
import json

# Create your views here.

class PieChartView(TemplateView):
	template_name = "autochart.html"

	def get(self, request, *args, **kwargs):
		context = super(PieChartView, self).get_context_data(**kwargs)
		dataframe_pk = request.GET.get('dataframe_id')
		column_name = request.GET.get('column_name')

		try:
			dataframe = DataFrame.objects.get(pk = dataframe_pk)
		except Exception,e:
			context['debug_content'] = str(e)
			return self.render_to_response(context)

		context['dataframe_name'] = dataframe.name
		context['column_name'] = column_name
		query_results, column_names = dataframe.query_results(
			"SELECT count(*), " + column_name + 
			" FROM " + dataframe.db_table_name +
			" GROUP BY " + column_name
		)

		context['query_results'] =  json.dumps(query_results)
		return self.render_to_response(context)

