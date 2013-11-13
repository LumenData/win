from django.views.generic import TemplateView
from data.models import DataFrame
from django.http import HttpResponse
import json
import sys
from pprint import pprint

# Create your views here.

class ChartBuilderView(TemplateView):
	template_name = "chart_builder.html"

	def get(self, request, *args, **kwargs):
		context = super(ChartBuilderView, self).get_context_data(**kwargs)
		column_names = request.GET.getlist("column_names[]");
		row_names = request.GET.getlist("row_names[]");

		try:
			dataframe = DataFrame.objects.get(pk = request.GET.get('dataframe_id'))
		except Exception,e:
			context['debug_content'] = str(e)
			return self.render_to_response(context)
			
		context['dataframe'] = dataframe

		return self.render_to_response(context)

class AutoChartView(TemplateView):
	template_name = "autochart.html"

	def get(self, request, *args, **kwargs):
		context = super(AutoChartView, self).get_context_data(**kwargs)
		
		dataframe_pk = request.GET.get('dataframe_id')
		column_names = request.GET.getlist("column_names[]");
		row_names = request.GET.getlist("row_names[]");

		try:
			dataframe = DataFrame.objects.get(pk = dataframe_pk)
		except Exception,e:
			context['debug_content'] = str(e)
			return self.render_to_response(context)
		
 		ncols = len(column_names)
 		nrows = len(row_names)

		if((nrows + ncols) == 0):
			context['contents'] = ""
		elif((nrows + ncols) == 1):
			column_name = row_names[0] if nrows > 0 else column_names[0]	
			query_results, tmp = dataframe.query_results(
				"SELECT %s `key`, count(*) y \n\
				FROM %s \n\
				GROUP BY 1" 
				% (column_name, dataframe.db_table_name)
			);
			
			chart_data = list(query_results)

			context['chartData'] = json.dumps(chart_data)
			context['chartType'] = 'pieChart';
# 			context['error_message'] = chart_data
		## Line Chart 				
		elif((nrows == 1) & (ncols == 1)):
		
			query_results, tmp = dataframe.query_results(
				"SELECT %s x, %s y \n\
				FROM %s \n\
				ORDER BY %s" 
				% (column_names[0], row_names[0], dataframe.db_table_name, column_names[0] )
			);

			query_results_as_list = list(query_results)
 			chart_data = [{"key": row_names[0], "values":  query_results_as_list}]

			context['chartData'] = json.dumps(chart_data)
			context['chartType'] = 'lineChart';
# 			context['error_message'] = chart_data;
		else:
			context['error_message'] = "That analysis type hasn't been implemented yet"
			
		context["debug_mode"] = request.GET.get('debug_mode')
		return self.render_to_response(context)

